"""Threshold Alert Rule - flags single transactions at or above the reporting threshold."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import LARGE_TX_THRESHOLD
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class ThresholdAlertRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Large Transaction Threshold"

    @property
    def description(self) -> str:
        return f"Flags individual transactions >= {LARGE_TX_THRESHOLD} EUR."

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "amount" not in transactions.columns:
            return alerts

        mask = transactions["amount"] >= LARGE_TX_THRESHOLD
        flagged = transactions[mask]

        for idx, row in flagged.iterrows():
            date_str = ""
            if "date" in transactions.columns:
                dt = pd.to_datetime(row.get("date"), errors="coerce")
                date_str = dt.strftime("%Y-%m-%d") if pd.notna(dt) else "unknown date"

            alerts.append(
                Alert(
                    id=str(uuid.uuid4()),
                    rule_name=self.rule_name,
                    severity=AlertSeverity.MEDIUM,
                    description=(
                        f"Transaction of {row['amount']:,.2f} EUR on {date_str} "
                        f"exceeds threshold of {LARGE_TX_THRESHOLD:,} EUR. "
                        f"Sender: {row.get('sender', 'N/A')}, Receiver: {row.get('receiver', 'N/A')}."
                    ),
                    affected_transaction_indices=[int(idx)],
                    alert_type=AlertType.THRESHOLD,
                )
            )

        return alerts
