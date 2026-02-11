"""Round Amount Pattern Rule - detects suspicious patterns of round-number transactions."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import (
    ROUND_AMOUNT_CONSECUTIVE_MIN,
    ROUND_AMOUNT_DIVISORS,
    ROUND_AMOUNT_RATIO,
)
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class RoundAmountPatternRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Round Amount Pattern"

    @property
    def description(self) -> str:
        return (
            f"Detects high ratio of round-amount transactions "
            f"(divisible by {'/'.join(str(d) for d in ROUND_AMOUNT_DIVISORS)}) "
            f"or {ROUND_AMOUNT_CONSECUTIVE_MIN}+ consecutive round amounts."
        )

    def _is_round(self, amount: float) -> bool:
        abs_amount = abs(amount)
        for divisor in ROUND_AMOUNT_DIVISORS:
            if abs_amount > 0 and abs_amount % divisor == 0:
                return True
        return False

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "amount" not in transactions.columns:
            return alerts

        df = transactions.copy()
        df["_is_round"] = df["amount"].apply(self._is_round)

        total = len(df)
        round_count = df["_is_round"].sum()

        if total == 0:
            return alerts

        ratio = round_count / total

        # Flag overall high ratio
        if ratio > ROUND_AMOUNT_RATIO and total >= 3:
            round_indices = df.index[df["_is_round"]].tolist()
            alerts.append(
                Alert(
                    id=str(uuid.uuid4()),
                    rule_name=self.rule_name,
                    severity=AlertSeverity.MEDIUM,
                    description=(
                        f"High round-amount ratio: {ratio:.0%} of transactions "
                        f"({round_count}/{total}) are round amounts "
                        f"(divisible by {' or '.join(str(d) for d in ROUND_AMOUNT_DIVISORS)})."
                    ),
                    affected_transaction_indices=[int(i) for i in round_indices],
                    alert_type=AlertType.ROUND_AMOUNT,
                )
            )

        # Flag consecutive round amounts
        if "date" in df.columns:
            df = df.sort_values("date").reset_index(drop=True)
            df["_is_round"] = df["amount"].apply(self._is_round)

        consecutive_start = None
        consecutive_count = 0

        for idx in range(len(df)):
            if df.loc[idx, "_is_round"]:
                if consecutive_start is None:
                    consecutive_start = idx
                consecutive_count += 1
            else:
                if consecutive_count >= ROUND_AMOUNT_CONSECUTIVE_MIN:
                    consec_indices = list(range(consecutive_start, consecutive_start + consecutive_count))
                    amounts = [df.loc[i, "amount"] for i in consec_indices]
                    alerts.append(
                        Alert(
                            id=str(uuid.uuid4()),
                            rule_name=self.rule_name,
                            severity=AlertSeverity.MEDIUM,
                            description=(
                                f"{consecutive_count} consecutive round-amount transactions detected: "
                                f"{', '.join(f'{a:,.2f}' for a in amounts)}."
                            ),
                            affected_transaction_indices=[int(i) for i in consec_indices],
                            alert_type=AlertType.ROUND_AMOUNT,
                        )
                    )
                consecutive_start = None
                consecutive_count = 0

        # Check last sequence
        if consecutive_count >= ROUND_AMOUNT_CONSECUTIVE_MIN and consecutive_start is not None:
            consec_indices = list(range(consecutive_start, consecutive_start + consecutive_count))
            amounts = [df.loc[i, "amount"] for i in consec_indices]
            alerts.append(
                Alert(
                    id=str(uuid.uuid4()),
                    rule_name=self.rule_name,
                    severity=AlertSeverity.MEDIUM,
                    description=(
                        f"{consecutive_count} consecutive round-amount transactions detected: "
                        f"{', '.join(f'{a:,.2f}' for a in amounts)}."
                    ),
                    affected_transaction_indices=[int(i) for i in consec_indices],
                    alert_type=AlertType.ROUND_AMOUNT,
                )
            )

        return alerts
