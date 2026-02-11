"""Singleton data store holding all uploaded DataFrames in memory."""

from __future__ import annotations

from typing import Optional

import pandas as pd


class DataStore:
    """Class-level singleton: all attributes are shared across the application."""

    transactions_df: Optional[pd.DataFrame] = None
    watchlist_df: Optional[pd.DataFrame] = None
    high_risk_countries_df: Optional[pd.DataFrame] = None
    work_instructions_df: Optional[pd.DataFrame] = None

    # ---- setters ----

    @classmethod
    def set_transactions(cls, df: pd.DataFrame) -> None:
        cls.transactions_df = df

    @classmethod
    def set_watchlist(cls, df: pd.DataFrame) -> None:
        cls.watchlist_df = df

    @classmethod
    def set_high_risk_countries(cls, df: pd.DataFrame) -> None:
        cls.high_risk_countries_df = df

    @classmethod
    def set_work_instructions(cls, df: pd.DataFrame) -> None:
        cls.work_instructions_df = df

    # ---- queries ----

    @classmethod
    def get_customer_transactions(cls, bcn: str) -> pd.DataFrame:
        """Return all transactions for a given business_contact_number."""
        if cls.transactions_df is None:
            return pd.DataFrame()
        mask = cls.transactions_df["business_contact_number"].astype(str) == str(bcn)
        return cls.transactions_df.loc[mask].reset_index(drop=True)

    @classmethod
    def search_bcn(cls, query: str) -> list[dict]:
        """Search BCNs by prefix and contains match.  Returns list of dicts
        with keys: bcn, name, transaction_count."""
        if cls.transactions_df is None:
            return []

        query_lower = query.strip().lower()
        if not query_lower:
            return []

        df = cls.transactions_df
        bcn_col = df["business_contact_number"].astype(str)

        # Prefix matches first, then contains matches
        prefix_mask = bcn_col.str.lower().str.startswith(query_lower)
        contains_mask = bcn_col.str.lower().str.contains(query_lower, na=False) & ~prefix_mask

        # Also search by sender name
        sender_col = df["sender"].astype(str)
        sender_mask = sender_col.str.lower().str.contains(query_lower, na=False) & ~prefix_mask & ~contains_mask

        combined_mask = prefix_mask | contains_mask | sender_mask

        if not combined_mask.any():
            return []

        matched = df.loc[combined_mask]
        grouped = matched.groupby("business_contact_number").agg(
            name=("sender", "first"),
            transaction_count=("sender", "size"),
        ).reset_index()

        # Determine ordering: prefix hits come first
        prefix_bcns = set(bcn_col[prefix_mask].unique())
        grouped["_is_prefix"] = grouped["business_contact_number"].isin(prefix_bcns)
        grouped = grouped.sort_values(["_is_prefix", "business_contact_number"], ascending=[False, True])
        grouped = grouped.drop(columns=["_is_prefix"])

        results: list[dict] = []
        for _, row in grouped.iterrows():
            results.append({
                "bcn": str(row["business_contact_number"]),
                "name": str(row["name"]),
                "transaction_count": int(row["transaction_count"]),
            })
        return results

    @classmethod
    def get_all_bcns(cls) -> list[str]:
        """Return a list of unique business contact numbers."""
        if cls.transactions_df is None:
            return []
        return (
            cls.transactions_df["business_contact_number"]
            .astype(str)
            .unique()
            .tolist()
        )

    @classmethod
    def get_upload_status(cls) -> dict:
        return {
            "transactions": cls.transactions_df is not None,
            "watchlist": cls.watchlist_df is not None,
            "high_risk_countries": cls.high_risk_countries_df is not None,
            "work_instructions": cls.work_instructions_df is not None,
        }

    @classmethod
    def clear_all(cls) -> None:
        cls.transactions_df = None
        cls.watchlist_df = None
        cls.high_risk_countries_df = None
        cls.work_instructions_df = None
