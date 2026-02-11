"""Pattern analyzer - compute transaction pattern statistics."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from models.schemas import PatternData


def analyze_patterns(
    transactions_df: pd.DataFrame,
    high_risk_countries_df: Optional[pd.DataFrame] = None,
) -> PatternData:
    """Analyze transaction patterns and return a PatternData object."""

    if transactions_df.empty:
        return PatternData()

    df = transactions_df.copy()

    # ---- By month ----
    by_month: dict[str, float] = {}
    if "date" in df.columns:
        df["_date"] = pd.to_datetime(df["date"], errors="coerce")
        valid_dates = df.dropna(subset=["_date"])
        if not valid_dates.empty:
            valid_dates = valid_dates.copy()
            valid_dates["_month"] = valid_dates["_date"].dt.strftime("%Y-%m")
            monthly = valid_dates.groupby("_month")["amount"].sum()
            by_month = {str(k): round(float(v), 2) for k, v in monthly.items()}

    # ---- By transaction type ----
    by_type: dict[str, float] = {}
    if "transaction_type" in df.columns:
        type_groups = df.groupby("transaction_type")["amount"].sum()
        by_type = {str(k): round(float(v), 2) for k, v in type_groups.items() if str(k).strip()}

    # ---- By currency ----
    by_currency: dict[str, float] = {}
    if "currency" in df.columns:
        currency_groups = df.groupby("currency")["amount"].sum()
        by_currency = {str(k): round(float(v), 2) for k, v in currency_groups.items() if str(k).strip()}

    # ---- Round amount ratio ----
    round_amount_ratio = 0.0
    if "amount" in df.columns and len(df) > 0:
        round_mask = df["amount"].apply(
            lambda x: abs(x) > 0 and (abs(x) % 1000 == 0 or abs(x) % 500 == 0)
        )
        round_amount_ratio = round(float(round_mask.sum() / len(df)), 4)

    # ---- Average transaction size ----
    avg_transaction_size = 0.0
    if "amount" in df.columns and len(df) > 0:
        avg_transaction_size = round(float(df["amount"].mean()), 2)

    # ---- High risk country exposure ----
    high_risk_country_exposure = 0.0
    if high_risk_countries_df is not None and not high_risk_countries_df.empty:
        if "country_code" in high_risk_countries_df.columns:
            hr_codes = set(
                high_risk_countries_df["country_code"]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
                .tolist()
            )

            if hr_codes and len(df) > 0:
                hr_count = 0
                for _, row in df.iterrows():
                    iban = str(row.get("iban", "")).strip().upper()
                    bic = str(row.get("bic", "")).strip().upper()

                    iban_country = iban[:2] if len(iban) >= 2 and iban[:2].isalpha() else ""
                    bic_country = bic[4:6] if len(bic) >= 6 and bic[4:6].isalpha() else ""

                    if iban_country in hr_codes or bic_country in hr_codes:
                        hr_count += 1

                high_risk_country_exposure = round(hr_count / len(df), 4)

    return PatternData(
        by_month=by_month,
        by_type=by_type,
        by_currency=by_currency,
        round_amount_ratio=round_amount_ratio,
        avg_transaction_size=avg_transaction_size,
        high_risk_country_exposure=high_risk_country_exposure,
    )
