"""Analysis router - alert and risk breakdown endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models.schemas import Alert, RiskAssessment
from services.aml_engine import AMLEngine
from services.data_store import DataStore
from services.risk_scorer import calculate_risk

router = APIRouter(prefix="/analysis", tags=["Analysis"])

_engine = AMLEngine()


@router.get("/{bcn}/alerts", response_model=list[Alert])
async def get_customer_alerts(bcn: str):
    """Return only the AML alerts for a customer."""
    tx_df = DataStore.get_customer_transactions(bcn)
    if tx_df.empty:
        raise HTTPException(status_code=404, detail=f"No transactions found for BCN '{bcn}'.")

    context = {
        "watchlist_df": DataStore.watchlist_df,
        "high_risk_countries_df": DataStore.high_risk_countries_df,
    }
    alerts = _engine.analyze(tx_df, context)
    return alerts


@router.get("/{bcn}/risk-breakdown", response_model=RiskAssessment)
async def get_risk_breakdown(bcn: str):
    """Return the risk assessment breakdown for a customer."""
    tx_df = DataStore.get_customer_transactions(bcn)
    if tx_df.empty:
        raise HTTPException(status_code=404, detail=f"No transactions found for BCN '{bcn}'.")

    context = {
        "watchlist_df": DataStore.watchlist_df,
        "high_risk_countries_df": DataStore.high_risk_countries_df,
    }
    alerts = _engine.analyze(tx_df, context)
    risk = calculate_risk(alerts)
    return risk
