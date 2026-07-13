"""
financial_report_consolidation_scanner.py

Scan page-level financial report text for multilingual consolidation-related terms,
capture +/- N pages around matches, merge overlapping page windows, and produce
LLM-ready chunks for extracting company / organization names.

Supported language signals:
- English
- Dutch
- French
- German

Input formats:
1. JSON file containing either:
   - a list of strings, one string per page
   - {"pages": ["page 1 text", "page 2 text", ...]}
   - {"pages": [{"page_number": 1, "text": "..."}, ...]}

2. Plain-text file where pages are separated by form-feed characters: \f

Usage:
    python financial_report_consolidation_scanner.py report_pages.json
    python financial_report_consolidation_scanner.py report_pages.json --context-pages 2
    python financial_report_consolidation_scanner.py report.txt --output results.json

The script uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


# ---------------------------------------------------------------------------
# Multilingual term configuration
# ---------------------------------------------------------------------------

STRONG_TERMS = {
    # English
    "consolidated financial statements",
    "consolidated accounts",
    "group financial statements",
    "group accounts",

    # Dutch
    "geconsolideerde jaarrekening",
    "geconsolideerde financiële staten",
    "geconsolideerde rekening",
    "geconsolideerde rekeningen",

    # French
    "comptes consolidés",
    "états financiers consolidés",
    "états financiers consolidées",

    # German
    "konzernabschluss",
    "konzernabschlüsse",
    "konzernrechnungslegung",
}

BROAD_TERMS = {
    # English
    "consolidated",
    "consolidation",

    # Dutch
    "geconsolideerd",
    "geconsolideerde",
    "consolidatie",

    # French
    "consolidé",
    "consolidée",
    "consolidés",
    "consolidées",
    "consolidation",

    # German
    "konsolidiert",
    "konsolidierte",
    "konsolidierter",
    "konsolidierten",
    "konsolidierung",
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Match:
    page_index: int          # 0-based
    page_number: int         # 1-based
    term: str
    signal: str              # "STRONG" or "BROAD"


@dataclass(frozen=True)
class PageWindow:
    start_page_index: int    # 0-based, inclusive
    end_page_index: int      # 0-based, inclusive


@dataclass
class LLMChunk:
    chunk_id: int
    start_page: int          # 1-based
    end_page: int            # 1-based
    matched_pages: List[int]
    matched_terms: List[str]
    strong_terms: List[str]
    broad_terms: List[str]
    text: str
    llm_prompt: str


# ---------------------------------------------------------------------------
# Normalization and matching
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize OCR/PDF text for robust multilingual matching.

    Steps:
    - lowercase
    - Unicode NFKD normalization
    - remove accents/diacritics
    - normalize whitespace

    Examples:
        "états financiers consolidés" -> "etats financiers consolides"
        "Konzernabschlüsse" -> "konzernabschlusse"
    """
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


NORMALIZED_STRONG_TERMS = {
    normalize_text(term): term for term in STRONG_TERMS
}

NORMALIZED_BROAD_TERMS = {
    normalize_text(term): term for term in BROAD_TERMS
}


def find_terms_on_page(page_text: str, page_index: int) -> List[Match]:
    """Find all configured strong and broad consolidation signals on one page."""
    normalized_page = normalize_text(page_text)
    matches: List[Match] = []

    for normalized_term, original_term in NORMALIZED_STRONG_TERMS.items():
        if normalized_term in normalized_page:
            matches.append(
                Match(
                    page_index=page_index,
                    page_number=page_index + 1,
                    term=original_term,
                    signal="STRONG",
                )
            )

    for normalized_term, original_term in NORMALIZED_BROAD_TERMS.items():
        if normalized_term in normalized_page:
            matches.append(
                Match(
                    page_index=page_index,
                    page_number=page_index + 1,
                    term=original_term,
                    signal="BROAD",
                )
            )

    return matches


def scan_pages(pages: Sequence[str]) -> List[Match]:
    """Scan all pages and return every matching term occurrence at page level."""
    all_matches: List[Match] = []

    for page_index, page_text in enumerate(pages):
        all_matches.extend(find_terms_on_page(page_text, page_index))

    return all_matches


# ---------------------------------------------------------------------------
# Page-window generation and merging
# ---------------------------------------------------------------------------

def build_page_windows(
    matching_page_indexes: Iterable[int],
    total_pages: int,
    context_pages: int = 2,
) -> List[PageWindow]:
    """
    Create +/- context page windows around matches and merge overlapping
    or directly adjacent windows.
    """
    if total_pages <= 0:
        return []

    unique_pages = sorted(set(matching_page_indexes))
    if not unique_pages:
        return []

    windows: List[PageWindow] = []

    for page_index in unique_pages:
        start = max(0, page_index - context_pages)
        end = min(total_pages - 1, page_index + context_pages)
        windows.append(PageWindow(start, end))

    merged: List[PageWindow] = [windows[0]]

    for current in windows[1:]:
        previous = merged[-1]

        if current.start_page_index <= previous.end_page_index + 1:
            merged[-1] = PageWindow(
                start_page_index=previous.start_page_index,
                end_page_index=max(
                    previous.end_page_index,
                    current.end_page_index,
                ),
            )
        else:
            merged.append(current)

    return merged


# ---------------------------------------------------------------------------
# LLM-ready chunk construction
# ---------------------------------------------------------------------------

def build_llm_prompt(
    chunk_text: str,
    start_page: int,
    end_page: int,
    matched_terms: Sequence[str],
) -> str:
    """Build an LLM prompt for company / organization extraction."""
    matched_terms_text = ", ".join(sorted(set(matched_terms)))

    return f"""
You are analyzing pages {start_page}-{end_page} of a financial report.

These pages were selected because they contain one or more
consolidation-related terms:

{matched_terms_text}

Your task:
1. Extract the reporting company or legal entity name.
2. Extract the consolidated group name, if present.
3. Extract the direct parent company, if present.
4. Extract the ultimate parent company, if present.
5. Extract subsidiaries or other group companies explicitly mentioned.
6. Distinguish entities that are merely mentioned from entities that are
   actually part of the reporting or consolidated group.
7. Determine whether the selected pages indicate that the current report
   contains consolidated financial statements, or merely refers to another
   entity's consolidated financial statements.

Return JSON only, using exactly this schema:

{{
  "reporting_entity": null,
  "consolidated_group_name": null,
  "direct_parent": null,
  "ultimate_parent": null,
  "subsidiaries": [],
  "other_organizations_mentioned": [],
  "is_current_document_consolidated": null,
  "evidence": [],
  "confidence": 0.0
}}

Rules:
- Do not invent organization names.
- Preserve the legal name exactly as written where possible.
- Use null when the answer cannot be determined.
- Use a confidence value between 0.0 and 1.0.
- Evidence should contain short verbatim snippets from the supplied text.

Financial report text:

{chunk_text}
""".strip()


def build_llm_chunks(
    pages: Sequence[str],
    matches: Sequence[Match],
    windows: Sequence[PageWindow],
) -> List[LLMChunk]:
    """Create merged page chunks with metadata and an LLM-ready prompt."""
    chunks: List[LLMChunk] = []

    for chunk_id, window in enumerate(windows, start=1):
        window_matches = [
            match
            for match in matches
            if window.start_page_index <= match.page_index <= window.end_page_index
        ]

        matched_pages = sorted({match.page_number for match in window_matches})
        matched_terms = sorted({match.term for match in window_matches})
        strong_terms = sorted({
            match.term for match in window_matches if match.signal == "STRONG"
        })
        broad_terms = sorted({
            match.term for match in window_matches if match.signal == "BROAD"
        })

        page_parts: List[str] = []
        for page_index in range(window.start_page_index, window.end_page_index + 1):
            page_parts.append(
                f"\n--- PAGE {page_index + 1} ---\n{pages[page_index]}"
            )

        chunk_text = "\n".join(page_parts).strip()
        start_page = window.start_page_index + 1
        end_page = window.end_page_index + 1

        chunks.append(
            LLMChunk(
                chunk_id=chunk_id,
                start_page=start_page,
                end_page=end_page,
                matched_pages=matched_pages,
                matched_terms=matched_terms,
                strong_terms=strong_terms,
                broad_terms=broad_terms,
                text=chunk_text,
                llm_prompt=build_llm_prompt(
                    chunk_text=chunk_text,
                    start_page=start_page,
                    end_page=end_page,
                    matched_terms=matched_terms,
                ),
            )
        )

    return chunks


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------

def load_pages_from_json(path: Path) -> List[str]:
    """
    Load page text from JSON.

    Supported formats:
        ["page 1 text", "page 2 text"]

        {"pages": ["page 1 text", "page 2 text"]}

        {
          "pages": [
            {"page_number": 1, "text": "page 1 text"},
            {"page_number": 2, "text": "page 2 text"}
          ]
        }
    """
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        raw_pages = data
    elif isinstance(data, dict) and "pages" in data:
        raw_pages = data["pages"]
    else:
        raise ValueError(
            "Unsupported JSON structure. Expected a list or an object "
            "containing a 'pages' field."
        )

    if not isinstance(raw_pages, list):
        raise ValueError("'pages' must be a list.")

    pages: List[str] = []

    for item in raw_pages:
        if isinstance(item, str):
            pages.append(item)
        elif isinstance(item, dict) and "text" in item:
            pages.append(str(item["text"]))
        else:
            raise ValueError(
                "Each page must be either a string or an object "
                "with a 'text' field."
            )

    return pages


def load_pages_from_text(path: Path) -> List[str]:
    """Load pages from plain text separated by form-feed characters."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.split("\f")


def load_pages(path: Path) -> List[str]:
    """Automatically choose JSON or plain-text input handling."""
    if path.suffix.lower() == ".json":
        return load_pages_from_json(path)
    return load_pages_from_text(path)


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_financial_report(
    pages: Sequence[str],
    context_pages: int = 2,
) -> dict:
    """
    Full pipeline:
    1. Scan all pages.
    2. Find multilingual consolidation signals.
    3. Build +/- context windows.
    4. Merge overlapping windows.
    5. Create LLM-ready chunks.
    """
    if context_pages < 0:
        raise ValueError("context_pages cannot be negative.")

    matches = scan_pages(pages)
    matching_page_indexes = [match.page_index for match in matches]

    windows = build_page_windows(
        matching_page_indexes=matching_page_indexes,
        total_pages=len(pages),
        context_pages=context_pages,
    )

    chunks = build_llm_chunks(
        pages=pages,
        matches=matches,
        windows=windows,
    )

    return {
        "summary": {
            "total_pages": len(pages),
            "total_term_matches": len(matches),
            "matching_pages": sorted({match.page_number for match in matches}),
            "merged_chunk_count": len(chunks),
            "context_pages": context_pages,
        },
        "matches": [asdict(match) for match in matches],
        "chunks": [asdict(chunk) for chunk in chunks],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan financial report pages for multilingual consolidation terms "
            "and create merged LLM-ready page chunks."
        )
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input JSON or plain-text file.",
    )

    parser.add_argument(
        "--context-pages",
        type=int,
        default=2,
        help="Number of pages before and after each matching page. Default: 2",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("consolidation_scan_results.json"),
        help="Output JSON path. Default: consolidation_scan_results.json",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    pages = load_pages(args.input_file)

    result = analyze_financial_report(
        pages=pages,
        context_pages=args.context_pages,
    )

    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = result["summary"]

    print(f"Total pages: {summary['total_pages']}")
    print(f"Matching pages: {summary['matching_pages']}")
    print(f"Total term matches: {summary['total_term_matches']}")
    print(f"Merged chunks: {summary['merged_chunk_count']}")
    print(f"Output written to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
