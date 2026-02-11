"""AML Engine - orchestrates all rule evaluations."""

from __future__ import annotations

from typing import Any

import pandas as pd

from models.enums import AlertSeverity
from models.schemas import Alert
from services.rules import (
    CounterpartyConcentrationRule,
    DormantAccountRule,
    FlowThroughRule,
    HighRiskCountryRule,
    ProfileDeviationRule,
    RapidFundMovementRule,
    RoundAmountPatternRule,
    StructuringDetectionRule,
    ThresholdAlertRule,
    WatchlistMatchRule,
)
from services.rules.base import AMLRule

# Severity ordering for sorting (highest first)
_SEVERITY_ORDER = {
    AlertSeverity.HIGH: 0,
    AlertSeverity.MEDIUM: 1,
    AlertSeverity.LOW: 2,
}


class AMLEngine:
    """Runs all AML rules against customer transactions and returns sorted alerts."""

    def __init__(self) -> None:
        self.rules: list[AMLRule] = [
            StructuringDetectionRule(),
            ThresholdAlertRule(),
            HighRiskCountryRule(),
            WatchlistMatchRule(),
            RapidFundMovementRule(),
            RoundAmountPatternRule(),
            DormantAccountRule(),
            CounterpartyConcentrationRule(),
            ProfileDeviationRule(),
            FlowThroughRule(),
        ]

    def analyze(
        self,
        transactions_df: pd.DataFrame,
        context: dict[str, Any],
    ) -> list[Alert]:
        """Run all rules and return alerts sorted by severity (highest first)."""
        all_alerts: list[Alert] = []

        for rule in self.rules:
            try:
                rule_alerts = rule.evaluate(transactions_df, context)
                all_alerts.extend(rule_alerts)
            except Exception as exc:
                # Log but don't crash - one broken rule shouldn't prevent others
                print(f"[AMLEngine] Rule '{rule.rule_name}' raised an exception: {exc}")

        # Sort by severity (HIGH > MEDIUM > LOW)
        all_alerts.sort(key=lambda a: _SEVERITY_ORDER.get(a.severity, 99))
        return all_alerts
