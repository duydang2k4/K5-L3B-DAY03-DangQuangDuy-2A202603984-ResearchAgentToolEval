from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Streamlit may inherit a legacy Windows console encoding from its launcher.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    execute_tool_call,
    now_iso,
    run_model_tool_loop,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


load_lab_env(ROOT)
PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
VERSION = "v5"
PROVIDER = os.getenv("DEMO_PROVIDER", "ollama")
TRANSCRIPTS_DIR = ROOT / "transcripts"


def init_session() -> None:
    if "demo_transcript" in st.session_state:
        return
    artifact = build_artifact_version(VERSION, PROMPT_PATH, TOOLS_PATH)
    transcript_id = f"{VERSION}_{PROVIDER}_ui_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}"
    st.session_state.demo_transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.demo_transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": PROVIDER,
        "model": os.getenv("OLLAMA_MODEL") if PROVIDER == "ollama" else None,
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "turns": [],
    }
    st.session_state.demo_history = []
    st.session_state.demo_messages = []
    st.session_state.pending_send = None


def save_turn(turn: dict[str, Any]) -> None:
    st.session_state.demo_transcript["turns"].append(turn)
    write_transcript(st.session_state.demo_transcript_path, st.session_state.demo_transcript)


def guarded_executor(call: ToolCall) -> dict[str, Any]:
    if call.name == "send":
        draft = str(call.args.get("text") or "").strip()
        if not draft:
            return {
                "tool": "send", "args": call.args,
                "result": {"error": "ValueError", "message": "No text to send"},
            }
        st.session_state.pending_send = draft
        return {
            "tool": "send", "args": call.args,
            "result": {
                "status": "needs_confirmation", "awaiting_user": True,
                "question": "Bạn kiểm tra bản nháp bên dưới rồi bấm Xác nhận gửi Telegram nếu đồng ý.",
            },
        }
    return execute_tool_call(call)


st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="centered")
st.title("🔎 Research Agent")
st.caption("Tìm nguồn, đọc bài, tra DOI và tổng hợp thông tin. Mọi lượt chat được lưu thành transcript JSON.")
init_session()

with st.sidebar:
    st.subheader("Phiên demo")
    st.write(f"Provider: **{PROVIDER}**")
    st.write(f"Model: **{st.session_state.demo_transcript['model'] or 'provider default'}**")
    st.write(f"Artifact: `{st.session_state.demo_transcript['artifact_version']}`")
    st.caption("Câu thử: 'Tra DOI 10.1038/nphys1170', 'Tóm tắt bài này', 'Đăng bản tin lên Telegram'.")
    st.download_button(
        "Tải transcript",
        data=Path(st.session_state.demo_transcript_path).read_bytes()
        if Path(st.session_state.demo_transcript_path).exists() else b"{}",
        file_name=Path(st.session_state.demo_transcript_path).name,
        mime="application/json",
    )

for message in st.session_state.demo_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("tool_events"):
            with st.expander("Tool calls & kết quả"):
                st.json(message["tool_events"])

if st.session_state.pending_send is not None:
    st.info("Agent đã đề xuất gửi nội dung sau. Bạn cần xác nhận bằng nút bên dưới.")
    st.code(st.session_state.pending_send, language=None)
    if st.button("Xác nhận gửi Telegram", type="primary"):
        draft = st.session_state.pending_send
        st.session_state.pending_send = None
        if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
            answer = "Chưa cấu hình Telegram bot/chat ID nên chưa thể gửi."
            event = {"tool": "send", "result": {"error": "missing_telegram_config"}}
        else:
            event = execute_tool_call(ToolCall(name="send", args={"text": draft, "confirmed": True}))
            result = event["result"]
            answer = "Đã gửi lên Telegram." if result.get("status") == "sent" else f"Gửi thất bại: {result.get('message', result.get('error'))}"
        st.session_state.demo_messages.append({"role": "assistant", "content": answer, "tool_events": [event]})
        save_turn({"turn_index": len(st.session_state.demo_transcript["turns"]) + 1,
                   "started_at": now_iso(), "user": "Xác nhận gửi Telegram trong UI",
                   "status": "answered", "assistant_text": answer,
                   "rounds": [], "tool_events": [event], "ended_at": now_iso()})
        st.rerun()
    if st.button("Hủy gửi"):
        st.session_state.pending_send = None
        st.rerun()

user_text = st.chat_input("Hỏi về tin tức, bài viết, paper hoặc chính sách...")
if user_text:
    st.session_state.demo_messages.append({"role": "user", "content": user_text})
    messages = [
        {"role": "system", "content": PROMPT_PATH.read_text(encoding="utf-8")},
        *trim_history(st.session_state.demo_history, 5),
        {"role": "user", "content": user_text},
    ]
    started_at = now_iso()
    try:
        result = run_model_tool_loop(
            provider=make_provider(PROVIDER), messages=messages,
            tools=to_openai_tools(load_tool_declarations(TOOLS_PATH)),
            model=None, max_tool_rounds=4, tool_executor=guarded_executor,
        )
        answer = result["assistant_text"]
        status = result["status"]
        events = result["tool_events"]
        rounds = result["rounds"]
        error = None
    except Exception as exc:
        answer = f"Lỗi kết nối hoặc provider: {type(exc).__name__}: {exc}"
        status = "provider_error"
        events, rounds, error = [], [], answer
    st.session_state.demo_messages.append({"role": "assistant", "content": answer, "tool_events": events})
    st.session_state.demo_history.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": answer},
    ])
    turn = {
        "turn_index": len(st.session_state.demo_transcript["turns"]) + 1,
        "started_at": started_at, "user": user_text, "status": status,
        "assistant_text": answer, "rounds": rounds, "tool_events": events,
        "ended_at": now_iso(),
    }
    if error:
        turn["error"] = error
    save_turn(turn)
    st.rerun()
