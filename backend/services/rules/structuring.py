"""Structuring Detection Rule - identifies transaction structuring (smurfing)."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import (
    STRUCTURING_LOWER_BOUND,
    STRUCTURING_MIN_TX,
    STRUCTURING_THRESHOLD,
    STRUCTURING_WINDOW_DAYS,
)
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class StructuringDetectionRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Structuring Detection"

    @property
    def description(self) -> str:
        return (
            "Detects potential structuring where multiple transactions are kept "
            f"below {STRUCTURING_THRESHOLD} within a rolling {STRUCTURING_WINDOW_DAYS}-day window."
        )

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "date" not in transactions.columns or "amount" not in transactions.columns:
            return alerts

        df = transactions.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

        if df.empty:
            return alerts

        # Filter to transactions in the structuring band
        band_mask = (df["amount"] >= STRUCTURING_LOWER_BOUND) & (df["amount"] < STRUCTURING_THRESHOLD)
        band_df = df[band_mask]

        if len(band_df) < STRUCTURING_MIN_TX:
            return alerts

        # Sliding window approach
        flagged_sets: list[set[int]] = []
        band_indices = band_df.index.tolist()

        for i, idx in enumerate(band_indices):
            window_start = df.loc[idx, "date"]
            window_end = window_start + pd.Timedelta(days=STRUCTURING_WINDOW_DAYS)

            cluster_indices: list[int] = []
            cluster_total = 0.0

            for j in range(i, len(band_indices)):
                jdx = band_indices[j]
                if df.loc[jdx, "date"] > window_end:
                    break
                cluster_indices.append(jdx)
                cluster_total += df.loc[jdx, "amount"]

            if len(cluster_indices) >= STRUCTURING_MIN_TX and cluster_total > STRUCTURING_THRESHOLD:
                cluster_set = frozenset(cluster_indices)
                # Avoid duplicate overlapping clusters
                if not any(cluster_set <= existing for existing in flagged_sets):
                    flagged_sets.append(set(cluster_indices))
                    amounts = [df.loc[k, "amount"] for k in cluster_indices]
                    dates = [df.loc[k, "date"].strftime("%Y-%m-%d") for k in cluster_indices]
                    alerts.append(
                        Alert(
                            id=str(uuid.uuid4()),
                            rule_name=self.rule_name,
                            severity=AlertSeverity.HIGH,
                            description=(
                                f"Potential structuring detected: {len(cluster_indices)} transactions "
                                f"between {dates[0]} and {dates[-1]} totalling "
                                f"{cluster_total:,.2f} EUR. Individual amounts: "
                                f"{', '.join(f'{a:,.2f}' for a in amounts)}"
                            ),
                            affected_transaction_indices=cluster_indices,
                            alert_type=AlertType.STRUCTURING,
                        )
                    )

        return alerts
