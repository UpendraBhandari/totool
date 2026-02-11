"""Parsing and validation logic for uploaded Excel files."""

from __future__ import annotations

import io
from typing import Tuple

import pandas as pd
from fastapi import UploadFile

from config import (
    REQUIRED_COLUMNS_HIGH_RISK_COUNTRIES,
    REQUIRED_COLUMNS_TRANSACTIONS,
    REQUIRED_COLUMNS_WATCHLIST,
    REQUIRED_COLUMNS_WORK_INSTRUCTIONS,
)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace, lowercase, replace spaces with underscores."""
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


async def _read_excel(file: UploadFile) -> pd.DataFrame:
    """Read an UploadFile into a DataFrame."""
    contents = await file.read()
    return pd.read_excel(io.BytesIO(contents), engine="openpyxl")


def _validate_columns(
    df: pd.DataFrame, required: list[str]
) -> list[str]:
    """Return a list of warning strings for any missing required columns."""
    present = set(df.columns)
    missing = [c for c in required if c not in present]
    warnings: list[str] = []
    if missing:
        warnings.append(f"Missing expected columns: {', '.join(missing)}")
    return warnings


# ---- Transactions ----

async def parse_transactions(file: UploadFile) -> Tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    df = await _read_excel(file)
    df = _normalize_columns(df)
    warnings.extend(_validate_columns(df, REQUIRED_COLUMNS_TRANSACTIONS))

    # Coerce types
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        nat_count = df["date"].isna().sum()
        if nat_count > 0:
            warnings.append(f"{nat_count} rows have unparseable dates")
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    if "business_contact_number" in df.columns:
        df["business_contact_number"] = df["business_contact_number"].astype(str).str.strip()

    # Fill NaN in string columns with empty string
    str_cols = ["sender", "receiver", "iban", "bic", "currency", "description", "transaction_type"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    return df, warnings


# ---- Watchlist ----

async def parse_watchlist(file: UploadFile) -> Tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    df = await _read_excel(file)
    df = _normalize_columns(df)
    warnings.extend(_validate_columns(df, REQUIRED_COLUMNS_WATCHLIST))

    if "name" in df.columns:
        df["name"] = df["name"].fillna("").astype(str).str.strip()

    return df, warnings


# ---- High Risk Countries ----

async def parse_high_risk_countries(file: UploadFile) -> Tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    df = await _read_excel(file)
    df = _normalize_columns(df)
    warnings.extend(_validate_columns(df, REQUIRED_COLUMNS_HIGH_RISK_COUNTRIES))

    if "country_code" in df.columns:
        df["country_code"] = df["country_code"].fillna("").astype(str).str.strip().str.upper()
    if "risk_level" in df.columns:
        df["risk_level"] = df["risk_level"].fillna("").astype(str).str.strip()

    return df, warnings


# ---- Work Instructions ----

async def parse_work_instructions(file: UploadFile) -> Tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    df = await _read_excel(file)
    df = _normalize_columns(df)
    warnings.extend(_validate_columns(df, REQUIRED_COLUMNS_WORK_INSTRUCTIONS))

    if "business_contact_number" in df.columns:
        df["business_contact_number"] = df["business_contact_number"].astype(str).str.strip()
    if "instruction" in df.columns:
        df["instruction"] = df["instruction"].fillna("").astype(str).str.strip()

    return df, warnings
