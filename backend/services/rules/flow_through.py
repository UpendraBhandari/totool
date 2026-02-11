"""Flow-Through Rule - detects pass-through / layering activity."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import (
    FLOW_THROUGH_MIN_AMOUNT,
    FLOW_THROUGH_VARIANCE,
    FLOW_THROUGH_WINDOW_DAYS,
)
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class FlowThroughRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Flow-Through Detection"

    @property
    def description(self) -> str:
        return (
            f"Detects pass-through activity where incoming ~ outgoing "
            f"(within {FLOW_THROUGH_VARIANCE:.0%} variance) over a {FLOW_THROUGH_WINDOW_DAYS}-day "
            f"window, totalling > {FLOW_THROUGH_MIN_AMOUNT} EUR."
        )

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "date" not in transactions.columns or "amount" not in transactions.columns:
            return alerts

        df = transactions.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

        if len(df) < 2:
            return alerts

        # Classify direction
        def classify(row: pd.Series) -> str:
            tt = str(row.get("transaction_type", "")).strip().lower()
            if tt in ("credit", "incoming", "deposit", "receive", "received"):
                return "in"
            if tt in ("debit", "outgoing", "withdrawal", "send", "sent", "transfer_out"):
                return "out"
            return "in" if row["amount"] >= 0 else "out"

        df["_direction"] = df.apply(classify, axis=1)

        # Use non-overlapping 30-day windows starting from the first transaction
        if df.empty:
            return alerts

        start_date = df["date"].min()
        end_date = df["date"].max()
        window = pd.Timedelta(days=FLOW_THROUGH_WINDOW_DAYS)

        current_start = start_date
        while current_start <= end_date:
            current_end = current_start + window
            window_mask = (df["date"] >= current_start) & (df["date"] < current_end)
            window_df = df[window_mask]

            if len(window_df) >= 2:
                total_in = window_df.loc[window_df["_direction"] == "in", "amount"].abs().sum()
                total_out = window_df.loc[window_df["_direction"] == "out", "amount"].abs().sum()
                total = max(total_in, total_out)

                if total >= FLOW_THROUGH_MIN_AMOUNT and total_in > 0 and total_out > 0:
                    variance = abs(total_in - total_out) / max(total_in, total_out)
                    if variance <= FLOW_THROUGH_VARIANCE:
                        window_indices = window_df.index.tolist()
                        alerts.append(
                            Alert(
                                id=str(uuid.uuid4()),
                                rule_name=self.rule_name,
                                severity=AlertSeverity.HIGH,
                                description=(
                                    f"Potential flow-through activity: "
                                    f"incoming {total_in:,.2f} EUR vs outgoing {total_out:,.2f} EUR "
                                    f"({variance:.1%} variance) between "
                                    f"{current_start.strftime('%Y-%m-%d')} and "
                                    f"{current_end.strftime('%Y-%m-%d')} "
                                    f"({len(window_df)} transactions)."
                                ),
                                affected_transaction_indices=[int(j) for j in window_indices],
                                alert_type=AlertType.FLOW_THROUGH,
                            )
                        )

            current_start = current_end

        return alerts
