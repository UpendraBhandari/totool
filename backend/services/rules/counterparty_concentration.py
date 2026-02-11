"""Counterparty Concentration Rule - detects fan-in and fan-out patterns."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import (
    COUNTERPARTY_AGGREGATE,
    COUNTERPARTY_UNIQUE_MIN,
    COUNTERPARTY_WINDOW_DAYS,
)
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class CounterpartyConcentrationRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Counterparty Concentration"

    @property
    def description(self) -> str:
        return (
            f"Detects fan-in/fan-out patterns: {COUNTERPARTY_UNIQUE_MIN}+ unique "
            f"counterparties within {COUNTERPARTY_WINDOW_DAYS} days with aggregate > "
            f"{COUNTERPARTY_AGGREGATE} EUR."
        )

    def _check_direction(
        self,
        df: pd.DataFrame,
        counterparty_col: str,
        label: str,
    ) -> list[Alert]:
        """Check fan-in or fan-out using a sliding window."""
        alerts: list[Alert] = []

        if counterparty_col not in df.columns:
            return alerts

        dates = df["date"].tolist()

        for i in range(len(df)):
            window_start = dates[i]
            window_end = window_start + pd.Timedelta(days=COUNTERPARTY_WINDOW_DAYS)

            window_mask = (df["date"] >= window_start) & (df["date"] <= window_end)
            window_df = df[window_mask]

            unique_counterparties = window_df[counterparty_col].str.strip().str.lower().unique()
            unique_counterparties = [c for c in unique_counterparties if c]

            if len(unique_counterparties) < COUNTERPARTY_UNIQUE_MIN:
                continue

            aggregate = window_df["amount"].sum()
            if aggregate <= COUNTERPARTY_AGGREGATE:
                continue

            window_indices = window_df.index.tolist()
            alerts.append(
                Alert(
                    id=str(uuid.uuid4()),
                    rule_name=self.rule_name,
                    severity=AlertSeverity.HIGH,
                    description=(
                        f"{label}: {len(unique_counterparties)} unique counterparties "
                        f"within {COUNTERPARTY_WINDOW_DAYS} days "
                        f"({window_start.strftime('%Y-%m-%d')} to {window_end.strftime('%Y-%m-%d')}), "
                        f"aggregate {aggregate:,.2f} EUR. "
                        f"Counterparties: {', '.join(sorted(set(unique_counterparties))[:10])}."
                    ),
                    affected_transaction_indices=[int(j) for j in window_indices],
                    alert_type=AlertType.COUNTERPARTY_CONCENTRATION,
                )
            )
            # Only report the first detected window per direction to avoid spam
            break

        return alerts

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "date" not in transactions.columns:
            return alerts

        df = transactions.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

        if df.empty:
            return alerts

        # Fan-in: many senders to the customer
        alerts.extend(self._check_direction(df, "sender", "Fan-in concentration"))

        # Fan-out: customer sends to many receivers
        alerts.extend(self._check_direction(df, "receiver", "Fan-out concentration"))

        return alerts
