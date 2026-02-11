"""Watchlist matcher - standalone fuzzy name matching utility."""

from __future__ import annotations

from typing import Optional

import pandas as pd
from rapidfuzz import fuzz, process

from config import FUZZY_MATCH_MEDIUM
from models.schemas import WatchlistMatch


def match_names(
    names: list[str],
    watchlist_df: pd.DataFrame,
    match_field: str,
    transaction_indices_map: Optional[dict[str, list[int]]] = None,
) -> list[WatchlistMatch]:
    """Match a list of entity names against watchlist entries.

    Parameters
    ----------
    names : list[str]
        Names to match (e.g. sender/receiver names).
    watchlist_df : pd.DataFrame
        Watchlist with at least a 'name' column.
    match_field : str
        Label describing the source field (e.g. "sender", "receiver").
    transaction_indices_map : dict, optional
        Mapping from name (lowered) to list of transaction indices where the name appears.

    Returns
    -------
    list[WatchlistMatch]
    """
    if watchlist_df is None or watchlist_df.empty or "name" not in watchlist_df.columns:
        return []

    watchlist_names = watchlist_df["name"].dropna().astype(str).str.strip().tolist()
    watchlist_names = [n for n in watchlist_names if n]

    if not watchlist_names or not names:
        return []

    if transaction_indices_map is None:
        transaction_indices_map = {}

    matches: list[WatchlistMatch] = []
    seen: set[tuple[str, str]] = set()

    for entity_name in names:
        entity_clean = entity_name.strip()
        if not entity_clean:
            continue

        results = process.extract(
            entity_clean,
            watchlist_names,
            scorer=fuzz.token_sort_ratio,
            limit=5,
        )

        for wl_name, score, _ in results:
            if score < FUZZY_MATCH_MEDIUM:
                continue

            dedup_key = (entity_clean.lower(), wl_name.lower())
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            tx_indices = transaction_indices_map.get(entity_clean.lower(), [])

            matches.append(
                WatchlistMatch(
                    matched_entity=entity_clean,
                    watchlist_entry=wl_name,
                    match_score=round(score, 1),
                    match_field=match_field,
                    transaction_indices=tx_indices,
                )
            )

    return matches
