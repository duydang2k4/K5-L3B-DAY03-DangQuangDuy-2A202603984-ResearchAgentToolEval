from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
TOOL_RESULTS_MAX_CHARS = 24_000
DEFAULT_CLARIFY_QUESTION = "Bạn bổ sung thêm thông tin nhé."
EXIT_COMMANDS = {"/exit", "/quit"}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip()).strip("_")
    return slug or "run"


def json_text(value: Any, *, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def summarize_calls(calls: list[ToolCall]) -> list[dict[str, Any]]:
    return [{"name": c.name, "args": c.args} for c in calls]


def trim_history(history: list[dict[str, str]], window: int) -> list[dict[str, str]]:
    return history[-window * 2:] if window > 0 else []


# --------------------------------------------------------------------------- #
# Tool execution & message builders
# --------------------------------------------------------------------------- #

def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if func is None:
        result: dict[str, Any] = {
            "error": "unknown_tool",
            "message": f"No local implementation for {call.name}",
        }
    else:
        try:
            result = func(**call.args)
        except Exception as exc:
            result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(events, max_chars=TOOL_RESULTS_MAX_CHARS)}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(summarize_calls(calls))}",
    }


# --------------------------------------------------------------------------- #
# Model <-> tool loop
# --------------------------------------------------------------------------- #

def run_model_tool_loop(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
    max_tool_rounds: int,
    tool_executor: Callable[[ToolCall], dict[str, Any]] = execute_tool_call,
) -> dict[str, Any]:
    working_messages = list(messages)
    rounds: list[dict[str, Any]] = []
    all_events: list[dict[str, Any]] = []

    def outcome(status: str, text: str) -> dict[str, Any]:
        return {
            "status": status,
            "assistant_text": text,
            "rounds": rounds,
            "tool_events": all_events,
        }

    for round_index in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        record: dict[str, Any] = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": summarize_calls(calls),
            "tool_results": [],
        }
        rounds.append(record)

        if not calls:
            return outcome("answered", response.text or "")

        working_messages.append(assistant_tool_message(response.text, calls))

        for call in calls:
            print(f"[tool] {call.name}({json.dumps(call.args, ensure_ascii=True, sort_keys=True)})")
            event = tool_executor(call)
            record["tool_results"].append(event)
            all_events.append(event)

            # Detect the clarification/pause tool by its output flag (rename-proof),
            # not by a hard-coded tool name.
            result = event.get("result")
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or DEFAULT_CLARIFY_QUESTION
                return outcome("waiting_for_user", question)

        working_messages.append(tool_results_message(record["tool_results"]))

    return outcome(
        "max_tool_rounds",
        f"Stopped after {max_tool_rounds} tool rounds. Inspect the transcript for details.",
    )


# --------------------------------------------------------------------------- #
# Transcript
# --------------------------------------------------------------------------- #

def write_transcript(path: Path, transcript: dict[str, Any]) -> None:
    transcript["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive Research Agent chat with transcript logging.")
    parser.add_argument("--provider", choices=PROVIDERS, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Student-chosen artifact version label, e.g. v0, v1, v2.")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5, help="Keep the last N user/assistant pairs in context.")
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    return parser


def new_transcript(args: argparse.Namespace, artifact_version: Any, model: str | None) -> tuple[Path, dict[str, Any]]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(args.version), safe_slug(args.provider), timestamp])
    path = args.transcripts_dir / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": args.provider,
        "model": model,
        "system_prompt": str(args.system_prompt),
        "tools": str(args.tools),
        "history_window": args.history_window,
        "max_tool_rounds": args.max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return path, transcript


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = build_arg_parser().parse_args()

    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(args.tools))
    provider = make_provider(args.provider)
    selected_model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)

    transcript_path, transcript = new_transcript(args, artifact_version, selected_model)

    print(f"Research Agent chat. artifact_version={artifact_version.artifact_version}")
    print("Type /exit to stop.")

    history: list[dict[str, str]] = []

    while True:
        try:
            user_text = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue
        if user_text in EXIT_COMMANDS:
            break

        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, args.history_window),
            {"role": "user", "content": user_text},
        ]
        turn: dict[str, Any] = {
            "turn_index": len(transcript["turns"]) + 1,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=args.model,
                max_tool_rounds=args.max_tool_rounds,
            )
        except Exception as exc:
            turn.update(status="provider_error", error=f"{type(exc).__name__}: {exc}")
            print(f"\nERROR> {turn['error']}")
        else:
            turn.update(result)
            print(f"\nAgent> {result['assistant_text']}")
            history += [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": result["assistant_text"]},
            ]

        turn["ended_at"] = now_iso()
        transcript["turns"].append(turn)
        write_transcript(transcript_path, transcript)
        print(f"Transcript saved: {transcript_path}")

    write_transcript(transcript_path, transcript)
    print(f"Final transcript: {transcript_path}")


if __name__ == "__main__":
    main()
