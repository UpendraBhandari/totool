"""Dormant Account Rule - detects burst activity after prolonged dormancy."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import (
    DORMANT_BURST_COUNT,
    DORMANT_BURST_WINDOW_DAYS,
    DORMANT_INACTIVITY_DAYS,
)
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class DormantAccountRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Dormant Account Activity"

    @property
    def description(self) -> str:
        return (
            f"Flags accounts with no activity for {DORMANT_INACTIVITY_DAYS}+ days "
            f"followed by {DORMANT_BURST_COUNT}+ transactions within {DORMANT_BURST_WINDOW_DAYS} days."
        )

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "date" not in transactions.columns:
            return alerts

        df = transactions.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

        if len(df) < DORMANT_BURST_COUNT + 1:
            return alerts

        # Find gaps of DORMANT_INACTIVITY_DAYS or more between consecutive transactions
        dates = df["date"].tolist()

        for i in range(1, len(dates)):
            gap_days = (dates[i] - dates[i - 1]).days
            if gap_days >= DORMANT_INACTIVITY_DAYS:
                # Found a dormancy gap. Now check for burst activity after the gap.
                burst_start = dates[i]
                burst_end = burst_start + pd.Timedelta(days=DORMANT_BURST_WINDOW_DAYS)

                burst_mask = (df["date"] >= burst_start) & (df["date"] <= burst_end)
                burst_df = df[burst_mask]

                if len(burst_df) >= DORMANT_BURST_COUNT:
                    burst_indices = burst_df.index.tolist()
                    burst_total = burst_df["amount"].sum()
                    alerts.append(
                        Alert(
                            id=str(uuid.uuid4()),
                            rule_name=self.rule_name,
                            severity=AlertSeverity.MEDIUM,
                            description=(
                                f"Dormant account reactivation: {gap_days} days of inactivity "
                                f"(last activity {dates[i-1].strftime('%Y-%m-%d')}), "
                                f"followed by {len(burst_df)} transactions within "
                                f"{DORMANT_BURST_WINDOW_DAYS} days starting "
                                f"{burst_start.strftime('%Y-%m-%d')}, "
                                f"totalling {burst_total:,.2f} EUR."
                            ),
                            affected_transaction_indices=[int(j) for j in burst_indices],
                            alert_type=AlertType.DORMANT_ACCOUNT,
                        )
                    )

        return alerts
