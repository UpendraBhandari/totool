"""AML Transaction Overview Tool - Configuration constants."""


# ---------- Structuring Detection ----------
STRUCTURING_THRESHOLD = 10000
STRUCTURING_LOWER_BOUND = 8000
STRUCTURING_WINDOW_DAYS = 7
STRUCTURING_MIN_TX = 3

# ---------- Large Transaction Threshold ----------
LARGE_TX_THRESHOLD = 10000

# ---------- Rapid Fund Movement ----------
RAPID_MOVEMENT_THRESHOLD = 5000
RAPID_MOVEMENT_WINDOW_HOURS = 48
RAPID_MOVEMENT_TOLERANCE = 0.20

# ---------- Round Amounts ----------
ROUND_AMOUNT_DIVISORS = [1000, 500]
ROUND_AMOUNT_RATIO = 0.60
ROUND_AMOUNT_CONSECUTIVE_MIN = 3

# ---------- Dormant Account ----------
DORMANT_INACTIVITY_DAYS = 90
DORMANT_BURST_COUNT = 3
DORMANT_BURST_WINDOW_DAYS = 7

# ---------- Counterparty Concentration ----------
COUNTERPARTY_UNIQUE_MIN = 5
COUNTERPARTY_WINDOW_DAYS = 14
COUNTERPARTY_AGGREGATE = 15000

# ---------- Profile Deviation ----------
PROFILE_DEVIATION_MULTIPLIER = 3.0

# ---------- Flow-Through ----------
FLOW_THROUGH_VARIANCE = 0.10
FLOW_THROUGH_WINDOW_DAYS = 30
FLOW_THROUGH_MIN_AMOUNT = 10000

# ---------- Fuzzy Match ----------
FUZZY_MATCH_HIGH = 85
FUZZY_MATCH_MEDIUM = 70

# ---------- Risk Weights ----------
RISK_WEIGHTS = {
    "structuring": 30,
    "high_risk_country_blacklist": 20,
    "high_risk_country_greylist": 10,
    "watchlist_high": 25,
    "watchlist_medium": 10,
    "threshold": 5,
    "rapid_movement": 20,
    "round_amount": 10,
    "dormant": 15,
    "counterparty": 20,
    "profile_deviation": 10,
    "flow_through": 25,
}

RISK_SCORE_CAP = 100

# ---------- Required Excel Columns ----------
REQUIRED_COLUMNS_TRANSACTIONS = [
    "date",
    "amount",
    "sender",
    "receiver",
    "iban",
    "bic",
    "currency",
    "description",
    "transaction_type",
    "business_contact_number",
]

REQUIRED_COLUMNS_WATCHLIST = [
    "name",
]

REQUIRED_COLUMNS_HIGH_RISK_COUNTRIES = [
    "country_code",
    "country_name",
    "risk_level",
]

REQUIRED_COLUMNS_WORK_INSTRUCTIONS = [
    "business_contact_number",
    "instruction",
]

# ---------- CORS ----------
CORS_ORIGINS = ["http://localhost:3000"]

# ---------- API ----------
API_V1_PREFIX = "/api/v1"
