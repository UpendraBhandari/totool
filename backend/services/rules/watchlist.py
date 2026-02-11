"""Watchlist Match Rule - fuzzy name matching against watchlist."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd
from rapidfuzz import fuzz

from config import FUZZY_MATCH_HIGH, FUZZY_MATCH_MEDIUM
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class WatchlistMatchRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Watchlist Match"

    @property
    def description(self) -> str:
        return "Matches transaction sender/receiver names against the watchlist using fuzzy matching."

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        wl_df = context.get("watchlist_df")
        if wl_df is None or wl_df.empty or "name" not in wl_df.columns:
            return alerts

        if transactions.empty:
            return alerts

        watchlist_names = wl_df["name"].dropna().astype(str).str.strip().tolist()
        watchlist_names = [n for n in watchlist_names if n]

        if not watchlist_names:
            return alerts

        # Track already-reported (entity, watchlist_entry) pairs to deduplicate
        seen: set[tuple[str, str]] = set()

        for field in ["sender", "receiver"]:
            if field not in transactions.columns:
                continue

            for idx, row in transactions.iterrows():
                entity_name = str(row[field]).strip()
                if not entity_name:
                    continue

                for wl_name in watchlist_names:
                    score = fuzz.token_sort_ratio(entity_name.lower(), wl_name.lower())

                    if score < FUZZY_MATCH_MEDIUM:
                        continue

                    dedup_key = (entity_name.lower(), wl_name.lower())
                    if dedup_key in seen:
                        # Still add the transaction index to the existing alert
                        for alert in alerts:
                            if (
                                alert.alert_type == AlertType.WATCHLIST_MATCH
                                and wl_name.lower() in alert.description.lower()
                                and entity_name.lower() in alert.description.lower()
                            ):
                                if int(idx) not in alert.affected_transaction_indices:
                                    alert.affected_transaction_indices.append(int(idx))
                                break
                        continue

                    seen.add(dedup_key)
                    severity = AlertSeverity.HIGH if score >= FUZZY_MATCH_HIGH else AlertSeverity.MEDIUM

                    alerts.append(
                        Alert(
                            id=str(uuid.uuid4()),
                            rule_name=self.rule_name,
                            severity=severity,
                            description=(
                                f"Watchlist match: '{entity_name}' ({field}) matches "
                                f"watchlist entry '{wl_name}' with score {score:.0f}%."
                            ),
                            affected_transaction_indices=[int(idx)],
                            alert_type=AlertType.WATCHLIST_MATCH,
                        )
                    )

        return alerts
