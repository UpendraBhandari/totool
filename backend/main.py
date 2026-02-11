"""AML Transaction Overview Tool - FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import API_V1_PREFIX, CORS_ORIGINS
from routers.analysis import router as analysis_router
from routers.customer import router as customer_router
from routers.upload import router as upload_router

app = FastAPI(
    title="AML Transaction Overview Tool",
    description="Backend API for Anti-Money Laundering transaction analysis and risk assessment.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router, prefix=API_V1_PREFIX)
app.include_router(customer_router, prefix=API_V1_PREFIX)
app.include_router(analysis_router, prefix=API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "name": "AML Transaction Overview Tool",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": API_V1_PREFIX,
        "endpoints": {
            "upload_transactions": f"{API_V1_PREFIX}/upload/transactions",
            "upload_watchlist": f"{API_V1_PREFIX}/upload/watchlist",
            "upload_high_risk_countries": f"{API_V1_PREFIX}/upload/high-risk-countries",
            "upload_work_instructions": f"{API_V1_PREFIX}/upload/work-instructions",
            "upload_status": f"{API_V1_PREFIX}/upload/status",
            "clear_data": f"{API_V1_PREFIX}/upload/clear",
            "customer_search": f"{API_V1_PREFIX}/customer/search",
            "customer_overview": f"{API_V1_PREFIX}/customer/{{bcn}}/overview",
            "customer_alerts": f"{API_V1_PREFIX}/analysis/{{bcn}}/alerts",
            "risk_breakdown": f"{API_V1_PREFIX}/analysis/{{bcn}}/risk-breakdown",
        },
    }
