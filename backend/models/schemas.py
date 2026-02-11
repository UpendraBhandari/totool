from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from models.enums import AlertSeverity, AlertType, RiskLevel


# ---- Core transaction record ----

class TransactionRecord(BaseModel):
    date: str
    amount: float
    sender: str
    receiver: str
    iban: Optional[str] = None
    bic: Optional[str] = None
    currency: str = "EUR"
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    business_contact_number: str


# ---- Alerts ----

class Alert(BaseModel):
    id: str
    rule_name: str
    severity: AlertSeverity
    description: str
    affected_transaction_indices: list[int] = Field(default_factory=list)
    alert_type: AlertType


# ---- Risk ----

class RiskAssessment(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    contributing_factors: list[str] = Field(default_factory=list)


# ---- Watchlist ----

class WatchlistMatch(BaseModel):
    matched_entity: str
    watchlist_entry: str
    match_score: float
    match_field: str
    transaction_indices: list[int] = Field(default_factory=list)


# ---- Patterns ----

class PatternData(BaseModel):
    by_month: dict[str, float] = Field(default_factory=dict)
    by_type: dict[str, float] = Field(default_factory=dict)
    by_currency: dict[str, float] = Field(default_factory=dict)
    round_amount_ratio: float = 0.0
    avg_transaction_size: float = 0.0
    high_risk_country_exposure: float = 0.0


# ---- Customer overview ----

class FlaggedTransaction(BaseModel):
    index: int
    date: str
    amount: float
    sender: str
    receiver: str
    iban: Optional[str] = None
    bic: Optional[str] = None
    currency: str = "EUR"
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    flags: list[str] = Field(default_factory=list)


class CustomerOverview(BaseModel):
    business_contact_number: str
    customer_name: Optional[str] = None
    risk_assessment: RiskAssessment
    transactions: list[FlaggedTransaction] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
    patterns: PatternData
    watchlist_matches: list[WatchlistMatch] = Field(default_factory=list)
    work_instructions: list[str] = Field(default_factory=list)


# ---- Upload ----

class UploadResponse(BaseModel):
    status: str
    record_count: int
    warnings: list[str] = Field(default_factory=list)


class UploadStatus(BaseModel):
    transactions: bool = False
    watchlist: bool = False
    high_risk_countries: bool = False
    work_instructions: bool = False


# ---- Search ----

class SearchResult(BaseModel):
    bcn: str
    name: str
    transaction_count: int
