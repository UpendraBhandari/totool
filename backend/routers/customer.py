"""Customer router - search and full customer overview endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

import pandas as pd

from models.schemas import (
    Alert,
    CustomerOverview,
    FlaggedTransaction,
    PatternData,
    SearchResult,
    WatchlistMatch,
)
from services.aml_engine import AMLEngine
from services.data_store import DataStore
from services.pattern_analyzer import analyze_patterns
from services.risk_scorer import calculate_risk
from services.watchlist_matcher import match_names

router = APIRouter(prefix="/customer", tags=["Customer"])

# Shared engine instance
_engine = AMLEngine()


@router.get("/search", response_model=list[SearchResult])
async def search_customers(q: str = Query(..., min_length=1, description="Search query")):
    """Search for customers by BCN or name."""
    results = DataStore.search_bcn(q)
    return [SearchResult(**r) for r in results]


@router.get("/{bcn}/overview", response_model=CustomerOverview)
async def get_customer_overview(bcn: str):
    """Full AML overview for a single customer."""

    # 1. Get customer transactions
    tx_df = DataStore.get_customer_transactions(bcn)
    if tx_df.empty:
        raise HTTPException(status_code=404, detail=f"No transactions found for BCN '{bcn}'.")

    # 2. Build context
    context = {
        "watchlist_df": DataStore.watchlist_df,
        "high_risk_countries_df": DataStore.high_risk_countries_df,
    }

    # 3. Run AML engine
    alerts: list[Alert] = _engine.analyze(tx_df, context)

    # 4. Calculate risk
    risk_assessment = calculate_risk(alerts)

    # 5. Analyze patterns
    patterns: PatternData = analyze_patterns(tx_df, DataStore.high_risk_countries_df)

    # 6. Watchlist matches (standalone utility for the overview)
    watchlist_matches: list[WatchlistMatch] = []
    if DataStore.watchlist_df is not None and not DataStore.watchlist_df.empty:
        # Build name -> indices map
        for field in ["sender", "receiver"]:
            if field not in tx_df.columns:
                continue
            names_list = tx_df[field].dropna().astype(str).str.strip().unique().tolist()
            names_list = [n for n in names_list if n]

            # Build index map
            idx_map: dict[str, list[int]] = {}
            for idx, row in tx_df.iterrows():
                name = str(row[field]).strip().lower()
                if name:
                    idx_map.setdefault(name, []).append(int(idx))

            field_matches = match_names(
                names=names_list,
                watchlist_df=DataStore.watchlist_df,
                match_field=field,
                transaction_indices_map=idx_map,
            )
            watchlist_matches.extend(field_matches)

    # 7. Work instructions
    work_instructions: list[str] = []
    if DataStore.work_instructions_df is not None and not DataStore.work_instructions_df.empty:
        wi_df = DataStore.work_instructions_df
        if "instruction" in wi_df.columns:
            if "business_contact_number" in wi_df.columns:
                mask = wi_df["business_contact_number"].astype(str) == str(bcn)
                filtered = wi_df.loc[mask]
                if not filtered.empty:
                    work_instructions = filtered["instruction"].dropna().astype(str).tolist()
                else:
                    # Return all instructions if no BCN-specific ones exist
                    work_instructions = wi_df["instruction"].dropna().astype(str).tolist()
            else:
                # No BCN column — return all instructions
                work_instructions = wi_df["instruction"].dropna().astype(str).tolist()

    # 8. Build flagged transactions
    # Collect which indices have flags from alerts
    index_flags: dict[int, list[str]] = {}
    for alert in alerts:
        for idx in alert.affected_transaction_indices:
            index_flags.setdefault(idx, []).append(alert.rule_name)

    flagged_transactions: list[FlaggedTransaction] = []
    for idx, row in tx_df.iterrows():
        date_str = ""
        if "date" in tx_df.columns:
            dt = pd.to_datetime(row.get("date"), errors="coerce")
            date_str = dt.strftime("%Y-%m-%d") if pd.notna(dt) else ""

        flagged_transactions.append(
            FlaggedTransaction(
                index=int(idx),
                date=date_str,
                amount=float(row.get("amount", 0)),
                sender=str(row.get("sender", "")),
                receiver=str(row.get("receiver", "")),
                iban=str(row.get("iban", "")) if row.get("iban") else None,
                bic=str(row.get("bic", "")) if row.get("bic") else None,
                currency=str(row.get("currency", "EUR")),
                description=str(row.get("description", "")) if row.get("description") else None,
                transaction_type=str(row.get("transaction_type", "")) if row.get("transaction_type") else None,
                flags=index_flags.get(int(idx), []),
            )
        )

    # Determine customer name from the first sender entry
    customer_name = str(tx_df.iloc[0].get("sender", "")) if not tx_df.empty else None

    return CustomerOverview(
        business_contact_number=bcn,
        customer_name=customer_name,
        risk_assessment=risk_assessment,
        transactions=flagged_transactions,
        alerts=alerts,
        patterns=patterns,
        watchlist_matches=watchlist_matches,
        work_instructions=work_instructions,
    )
