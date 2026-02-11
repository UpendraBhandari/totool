"""Rapid Fund Movement Rule - detects quick in-out fund transfers."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import (
    RAPID_MOVEMENT_THRESHOLD,
    RAPID_MOVEMENT_TOLERANCE,
    RAPID_MOVEMENT_WINDOW_HOURS,
)
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class RapidFundMovementRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Rapid Fund Movement"

    @property
    def description(self) -> str:
        return (
            f"Detects rapid in-out fund movements >= {RAPID_MOVEMENT_THRESHOLD} EUR "
            f"within {RAPID_MOVEMENT_WINDOW_HOURS} hours."
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

        # Classify transactions as incoming or outgoing based on transaction_type
        # Common conventions: credit/incoming/deposit vs debit/outgoing/withdrawal
        def classify(row: pd.Series) -> str:
            tt = str(row.get("transaction_type", "")).strip().lower()
            if tt in ("credit", "incoming", "deposit", "receive", "received"):
                return "in"
            if tt in ("debit", "outgoing", "withdrawal", "send", "sent", "transfer_out"):
                return "out"
            # Fallback: positive amounts as incoming
            return "in" if row["amount"] >= 0 else "out"

        df["direction"] = df.apply(classify, axis=1)

        incoming = df[df["direction"] == "in"]
        outgoing = df[df["direction"] == "out"]

        flagged_pairs: set[tuple[int, int]] = set()

        # Check incoming followed by outgoing (receive then send)
        for in_idx, in_row in incoming.iterrows():
            if abs(in_row["amount"]) < RAPID_MOVEMENT_THRESHOLD:
                continue
            for out_idx, out_row in outgoing.iterrows():
                if abs(out_row["amount"]) < RAPID_MOVEMENT_THRESHOLD:
                    continue
                pair = (min(int(in_idx), int(out_idx)), max(int(in_idx), int(out_idx)))
                if pair in flagged_pairs:
                    continue

                time_diff = abs((out_row["date"] - in_row["date"]).total_seconds()) / 3600
                if time_diff > RAPID_MOVEMENT_WINDOW_HOURS:
                    continue

                in_amt = abs(in_row["amount"])
                out_amt = abs(out_row["amount"])
                if in_amt == 0:
                    continue

                diff_ratio = abs(in_amt - out_amt) / in_amt
                if diff_ratio <= RAPID_MOVEMENT_TOLERANCE:
                    flagged_pairs.add(pair)
                    direction_label = (
                        "received then sent" if in_row["date"] <= out_row["date"] else "sent then received"
                    )
                    alerts.append(
                        Alert(
                            id=str(uuid.uuid4()),
                            rule_name=self.rule_name,
                            severity=AlertSeverity.HIGH,
                            description=(
                                f"Rapid fund movement: {direction_label}. "
                                f"In: {in_amt:,.2f} EUR on {in_row['date'].strftime('%Y-%m-%d %H:%M')}, "
                                f"Out: {out_amt:,.2f} EUR on {out_row['date'].strftime('%Y-%m-%d %H:%M')} "
                                f"({time_diff:.1f} hours apart, {diff_ratio:.1%} variance)."
                            ),
                            affected_transaction_indices=[int(in_idx), int(out_idx)],
                            alert_type=AlertType.RAPID_MOVEMENT,
                        )
                    )

        # Check outgoing followed by incoming (reverse direction)
        for out_idx, out_row in outgoing.iterrows():
            if abs(out_row["amount"]) < RAPID_MOVEMENT_THRESHOLD:
                continue
            for in_idx, in_row in incoming.iterrows():
                if abs(in_row["amount"]) < RAPID_MOVEMENT_THRESHOLD:
                    continue
                if in_row["date"] <= out_row["date"]:
                    continue  # Already covered above
                pair = (min(int(out_idx), int(in_idx)), max(int(out_idx), int(in_idx)))
                if pair in flagged_pairs:
                    continue

                time_diff = abs((in_row["date"] - out_row["date"]).total_seconds()) / 3600
                if time_diff > RAPID_MOVEMENT_WINDOW_HOURS:
                    continue

                out_amt = abs(out_row["amount"])
                in_amt = abs(in_row["amount"])
                if out_amt == 0:
                    continue

                diff_ratio = abs(out_amt - in_amt) / out_amt
                if diff_ratio <= RAPID_MOVEMENT_TOLERANCE:
                    flagged_pairs.add(pair)
                    alerts.append(
                        Alert(
                            id=str(uuid.uuid4()),
                            rule_name=self.rule_name,
                            severity=AlertSeverity.HIGH,
                            description=(
                                f"Rapid fund movement: sent then received. "
                                f"Out: {out_amt:,.2f} EUR on {out_row['date'].strftime('%Y-%m-%d %H:%M')}, "
                                f"In: {in_amt:,.2f} EUR on {in_row['date'].strftime('%Y-%m-%d %H:%M')} "
                                f"({time_diff:.1f} hours apart, {diff_ratio:.1%} variance)."
                            ),
                            affected_transaction_indices=[int(out_idx), int(in_idx)],
                            alert_type=AlertType.RAPID_MOVEMENT,
                        )
                    )

        return alerts
