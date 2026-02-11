"""High Risk Country Rule - flags transactions involving high-risk jurisdictions."""

from __future__ import annotations

import uuid
from typing import Any

import pandas as pd

from models.enums import AlertSeverity, AlertType
from models.schemas import Alert
from services.rules.base import AMLRule


class HighRiskCountryRule(AMLRule):

    @property
    def rule_name(self) -> str:
        return "High Risk Country"

    @property
    def description(self) -> str:
        return "Flags transactions involving IBANs or BICs from high-risk countries."

    def _extract_country_iban(self, iban: str) -> str:
        """First 2 characters of IBAN are the country code."""
        iban = str(iban).strip().upper()
        if len(iban) >= 2 and iban[:2].isalpha():
            return iban[:2]
        return ""

    def _extract_country_bic(self, bic: str) -> str:
        """Characters 5-6 (0-indexed 4:6) of a BIC are the country code."""
        bic = str(bic).strip().upper()
        if len(bic) >= 6 and bic[4:6].isalpha():
            return bic[4:6]
        return ""

    def evaluate(self, transactions: pd.DataFrame, context: dict[str, Any]) -> list[Alert]:
        alerts: list[Alert] = []

        hr_df = context.get("high_risk_countries_df")
        if hr_df is None or hr_df.empty:
            return alerts

        if transactions.empty:
            return alerts

        # Build lookup: country_code -> risk_level
        risk_lookup: dict[str, str] = {}
        if "country_code" in hr_df.columns and "risk_level" in hr_df.columns:
            for _, row in hr_df.iterrows():
                code = str(row["country_code"]).strip().upper()
                level = str(row["risk_level"]).strip()
                if code:
                    risk_lookup[code] = level

        if not risk_lookup:
            return alerts

        for idx, row in transactions.iterrows():
            countries_found: list[tuple[str, str]] = []  # (country_code, source)

            if "iban" in transactions.columns:
                cc = self._extract_country_iban(row.get("iban", ""))
                if cc and cc in risk_lookup:
                    countries_found.append((cc, "IBAN"))

            if "bic" in transactions.columns:
                cc = self._extract_country_bic(row.get("bic", ""))
                if cc and cc in risk_lookup:
                    countries_found.append((cc, "BIC"))

            for cc, source in countries_found:
                risk_level_str = risk_lookup[cc]
                is_blacklist = "blacklist" in risk_level_str.lower()
                severity = AlertSeverity.HIGH if is_blacklist else AlertSeverity.MEDIUM
                label = "Blacklisted" if is_blacklist else "Greylisted"

                date_str = ""
                if "date" in transactions.columns:
                    dt = pd.to_datetime(row.get("date"), errors="coerce")
                    date_str = dt.strftime("%Y-%m-%d") if pd.notna(dt) else "unknown date"

                alerts.append(
                    Alert(
                        id=str(uuid.uuid4()),
                        rule_name=self.rule_name,
                        severity=severity,
                        description=(
                            f"{label} country {cc} detected via {source} on transaction "
                            f"dated {date_str}, amount {row.get('amount', 0):,.2f} EUR. "
                            f"Sender: {row.get('sender', 'N/A')}, Receiver: {row.get('receiver', 'N/A')}."
                        ),
                        affected_transaction_indices=[int(idx)],
                        alert_type=AlertType.HIGH_RISK_COUNTRY,
                    )
                )

        return alerts
