"""Upload router - endpoints for uploading and managing data files."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File

from models.schemas import UploadResponse, UploadStatus
from services.data_store import DataStore
from services.excel_parser import (
    parse_high_risk_countries,
    parse_transactions,
    parse_watchlist,
    parse_work_instructions,
)

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}


def _validate_extension(filename: str | None) -> None:
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Only .xlsx and .xls are accepted.",
        )


# ---- Upload endpoints ----

@router.post("/transactions", response_model=UploadResponse)
async def upload_transactions(file: UploadFile = File(...)):
    """Upload customer transaction data (Excel)."""
    _validate_extension(file.filename)
    df, warnings = await parse_transactions(file)
    DataStore.set_transactions(df)
    return UploadResponse(status="success", record_count=len(df), warnings=warnings)


@router.post("/watchlist", response_model=UploadResponse)
async def upload_watchlist(file: UploadFile = File(...)):
    """Upload watchlist data (Excel)."""
    _validate_extension(file.filename)
    df, warnings = await parse_watchlist(file)
    DataStore.set_watchlist(df)
    return UploadResponse(status="success", record_count=len(df), warnings=warnings)


@router.post("/high-risk-countries", response_model=UploadResponse)
async def upload_high_risk_countries(file: UploadFile = File(...)):
    """Upload high-risk countries data (Excel)."""
    _validate_extension(file.filename)
    df, warnings = await parse_high_risk_countries(file)
    DataStore.set_high_risk_countries(df)
    return UploadResponse(status="success", record_count=len(df), warnings=warnings)


@router.post("/work-instructions", response_model=UploadResponse)
async def upload_work_instructions(file: UploadFile = File(...)):
    """Upload work instructions data (Excel)."""
    _validate_extension(file.filename)
    df, warnings = await parse_work_instructions(file)
    DataStore.set_work_instructions(df)
    return UploadResponse(status="success", record_count=len(df), warnings=warnings)


# ---- Status / Clear ----

@router.get("/status", response_model=UploadStatus)
async def get_upload_status():
    """Return which data files have been uploaded."""
    return UploadStatus(**DataStore.get_upload_status())


@router.delete("/clear")
async def clear_all_data():
    """Clear all uploaded data from memory."""
    DataStore.clear_all()
    return {"status": "cleared", "message": "All data has been removed from memory."}
