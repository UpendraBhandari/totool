"""Profile Deviation Rule - detects transactions deviating from historical patterns."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from config import PROFILE_DEVIATION_MULTIPLIER
from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class ProfileDeviationRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "Profile Deviation"

    @property
    def description(self) -> str:
        return (
            f"Flags transactions exceeding {PROFILE_DEVIATION_MULTIPLIER}x the "
            "historical average amount or monthly frequency."
        )

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        if transactions.empty or "amount" not in transactions.columns:
            return alerts

        df = transactions.copy()

        # ---- Amount deviation ----
        avg_amount = df["amount"].mean()
        if avg_amount > 0:
            threshold = avg_amount * PROFILE_DEVIATION_MULTIPLIER
            high_mask = df["amount"] > threshold
            for idx in df.index[high_mask]:
                row = df.loc[idx]
                date_str = ""
                if "date" in df.columns:
                    dt = pd.to_datetime(row.get("date"), errors="coerce")
                    date_str = dt.strftime("%Y-%m-%d") if pd.notna(dt) else "unknown date"

                alerts.append(
                    Alert(
                        id=str(uuid.uuid4()),
                        rule_name=self.rule_name,
                        severity=AlertSeverity.MEDIUM,
                        description=(
                            f"Amount deviation: transaction of {row['amount']:,.2f} EUR on "
                            f"{date_str} is {row['amount']/avg_amount:.1f}x the historical "
                            f"average of {avg_amount:,.2f} EUR "
                            f"(threshold: {PROFILE_DEVIATION_MULTIPLIER}x)."
                        ),
                        affected_transaction_indices=[int(idx)],
                        alert_type=AlertType.PROFILE_DEVIATION,
                    )
                )

        # ---- Frequency deviation ----
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df_valid = df.dropna(subset=["date"])
            if not df_valid.empty:
                df_valid = df_valid.copy()
                df_valid["_month"] = df_valid["date"].dt.to_period("M")
                monthly_counts = df_valid.groupby("_month").size()

                if len(monthly_counts) >= 2:
                    avg_frequency = monthly_counts.mean()
                    freq_threshold = avg_frequency * PROFILE_DEVIATION_MULTIPLIER

                    for period, count in monthly_counts.items():
                        if count > freq_threshold:
                            month_mask = df_valid["_month"] == period
                            month_indices = df_valid.index[month_mask].tolist()
                            alerts.append(
                                Alert(
                                    id=str(uuid.uuid4()),
                                    rule_name=self.rule_name,
                                    severity=AlertSeverity.MEDIUM,
                                    description=(
                                        f"Frequency deviation: {count} transactions in "
                                        f"{period} is {count/avg_frequency:.1f}x the average "
                                        f"monthly frequency of {avg_frequency:.1f} "
                                        f"(threshold: {PROFILE_DEVIATION_MULTIPLIER}x)."
                                    ),
                                    affected_transaction_indices=[int(j) for j in month_indices],
                                    alert_type=AlertType.PROFILE_DEVIATION,
                                )
                            )

        return alerts
