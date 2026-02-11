"""Risk scoring module - computes overall risk from alerts."""

from __future__ import annotations

from models.enums import AlertSeverity, AlertType, RiskLevel
from models.schemas import Alert, RiskAssessment
from config import RISK_SCORE_CAP, RISK_WEIGHTS


def _map_alert_to_weight_key(alert: Alert) -> str | None:
    """Map an Alert to the corresponding key in RISK_WEIGHTS."""
    at = alert.alert_type
    sev = alert.severity

    if at == AlertType.STRUCTURING:
        return "structuring"
    if at == AlertType.THRESHOLD:
        return "threshold"
    if at == AlertType.HIGH_RISK_COUNTRY:
        if sev == AlertSeverity.HIGH:
            return "high_risk_country_blacklist"
        return "high_risk_country_greylist"
    if at == AlertType.WATCHLIST_MATCH:
        if sev == AlertSeverity.HIGH:
            return "watchlist_high"
        return "watchlist_medium"
    if at == AlertType.RAPID_MOVEMENT:
        return "rapid_movement"
    if at == AlertType.ROUND_AMOUNT:
        return "round_amount"
    if at == AlertType.DORMANT_ACCOUNT:
        return "dormant"
    if at == AlertType.COUNTERPARTY_CONCENTRATION:
        return "counterparty"
    if at == AlertType.PROFILE_DEVIATION:
        return "profile_deviation"
    if at == AlertType.FLOW_THROUGH:
        return "flow_through"

    return None


def _score_to_level(score: float) -> RiskLevel:
    if score <= 25:
        return RiskLevel.LOW
    if score <= 50:
        return RiskLevel.MEDIUM
    if score <= 75:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def calculate_risk(alerts: list[Alert]) -> RiskAssessment:
    """Weighted risk scoring.  Each distinct risk category contributes its weight
    at most once (i.e. multiple structuring alerts still only add 30 points)."""

    triggered: dict[str, float] = {}
    contributing_factors: list[str] = []

    for alert in alerts:
        key = _map_alert_to_weight_key(alert)
        if key is None:
            continue
        weight = RISK_WEIGHTS.get(key, 0)
        if key not in triggered:
            triggered[key] = weight
            contributing_factors.append(
                f"{alert.rule_name} ({alert.severity.value}): +{weight} points"
            )

    raw_score = sum(triggered.values())
    capped_score = min(raw_score, RISK_SCORE_CAP)

    return RiskAssessment(
        overall_score=capped_score,
        risk_level=_score_to_level(capped_score),
        contributing_factors=contributing_factors,
    )
