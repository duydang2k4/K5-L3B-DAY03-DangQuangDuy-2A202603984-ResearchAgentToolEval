from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err


def lookup_doi(doi: str = "") -> dict[str, Any]:
    """Return Crossref bibliographic metadata for an exact DOI."""
    try:
        if not isinstance(doi, str):
            raise ValueError("doi must be a string")
        normalized = doi.strip()
        normalized = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", normalized, flags=re.IGNORECASE)
        normalized = normalized.strip()
        if not re.fullmatch(r"10\.\d{4,9}/\S+", normalized, flags=re.IGNORECASE):
            raise ValueError("doi must be a valid DOI such as 10.1038/nphys1170")

        response = requests.get(
            f"https://api.crossref.org/works/{quote(normalized, safe='/')}",
            headers={"User-Agent": "ResearchAgentToolEval/1.0 (educational lab)"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        message = response.json().get("message")
        if not isinstance(message, dict):
            raise ValueError("Crossref response has no message object")

        authors = [
            " ".join(part for part in (author.get("given"), author.get("family")) if part)
            for author in message.get("author", [])
            if isinstance(author, dict)
        ]
        date_parts = message.get("published", {}).get("date-parts", [])
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        return {
            "tool": "doi_lookup",
            "doi": message.get("DOI", normalized),
            "title": (message.get("title") or [""])[0],
            "authors": authors,
            "year": year,
            "journal": (message.get("container-title") or [""])[0],
            "url": message.get("URL", f"https://doi.org/{normalized}"),
            "citation_count": message.get("is-referenced-by-count"),
            "source": "Crossref",
        }
    except Exception as exc:
        return err("doi_lookup", exc)
