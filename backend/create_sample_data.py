"""Generate sample Excel files with deliberately suspicious patterns to test all 10 AML rules."""
import pandas as pd
from datetime import datetime, timedelta
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Transactions ──────────────────────────────────────────────────────────────
rows = []

def add(date, amount, sender, receiver, iban, bic, currency, desc, tx_type, bcn):
    rows.append({
        'Date': date, 'Amount': amount, 'Sender': sender, 'Receiver': receiver,
        'IBAN': iban, 'BIC': bic, 'Currency': currency,
        'Description': desc, 'Transaction Type': tx_type,
        'Business Contact Number': bcn,
    })

# ── BCN-001: "Jan de Vries" — triggers structuring, round amounts, threshold ──
base = datetime(2024, 1, 5)
# Structuring: 4 txns just below €10k in 5 days (Rule 1)
add(base, 9500, 'Jan de Vries', 'Alpha Trading BV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Payment for goods', 'Transfer', 'BCN-001')
add(base + timedelta(days=1), 9200, 'Jan de Vries', 'Alpha Trading BV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Invoice 1042', 'Transfer', 'BCN-001')
add(base + timedelta(days=2), 9800, 'Jan de Vries', 'Beta Services Ltd', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Consulting fee', 'Transfer', 'BCN-001')
add(base + timedelta(days=4), 8500, 'Jan de Vries', 'Alpha Trading BV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Material costs', 'Transfer', 'BCN-001')

# Large threshold tx (Rule 2) + round amount
add(base + timedelta(days=20), 25000, 'Jan de Vries', 'Gamma Holdings NV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Investment', 'Transfer', 'BCN-001')

# Round amounts pattern (Rule 6): many round amounts
for i in range(8):
    add(base + timedelta(days=30 + i*3), 5000, 'Jan de Vries', 'Delta Corp', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Payment {i+1}', 'Transfer', 'BCN-001')

# Normal transactions for baseline
for i in range(5):
    add(base + timedelta(days=60 + i*7), 1234.56 + i*100, 'Jan de Vries', 'Local Shop BV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Regular purchase {i+1}', 'Purchase', 'BCN-001')


# ── BCN-002: "Maria Petrova" — triggers high-risk country, rapid movement, flow-through ──
base2 = datetime(2024, 2, 1)

# High-risk country (Rule 3): transactions to/from Iran, Syria
add(base2, 15000, 'Maria Petrova', 'Tehran Import Co', 'IR060550000000123456789', 'BMJIIRTH', 'EUR', 'Import goods', 'International Transfer', 'BCN-002')
add(base2 + timedelta(days=5), 12000, 'Damascus Trading', 'Maria Petrova', 'SY0200010000000123456789', 'CBSYSYDA', 'EUR', 'Export payment', 'International Transfer', 'BCN-002')
add(base2 + timedelta(days=10), 8000, 'Maria Petrova', 'Minsk Partners', 'BY13NBRB0000000000000190', 'NBRBBY2X', 'EUR', 'Service fee', 'International Transfer', 'BCN-002')

# Rapid fund movement (Rule 5): receive then send within 48h
add(base2 + timedelta(days=20), 20000, 'External Source AG', 'Maria Petrova', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'Incoming transfer', 'Credit', 'BCN-002')
add(base2 + timedelta(days=20, hours=18), 19500, 'Maria Petrova', 'Offshore Ltd', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Outgoing transfer', 'Debit', 'BCN-002')

# More rapid movement
add(base2 + timedelta(days=30), 15000, 'Swiss Bank Corp', 'Maria Petrova', 'CH9300762011623852957', 'UBSWCHZH', 'EUR', 'Wire transfer', 'Credit', 'BCN-002')
add(base2 + timedelta(days=30, hours=6), 14200, 'Maria Petrova', 'Caribbean Holdings', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Investment', 'Debit', 'BCN-002')

# Flow-through pattern (Rule 10): in ≈ out over 30 days
for i in range(6):
    add(base2 + timedelta(days=40 + i*4), 5000 + i*200, 'Various Sender ' + str(i+1), 'Maria Petrova', 'DE89370400440532013000', 'COBADEFF', 'EUR', f'Incoming {i+1}', 'Credit', 'BCN-002')
for i in range(5):
    add(base2 + timedelta(days=42 + i*5), 6000 + i*100, 'Maria Petrova', f'Recipient {i+1}', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Outgoing {i+1}', 'Debit', 'BCN-002')


# ── BCN-003: "Ahmed Al-Rashid" — triggers watchlist, counterparty concentration, profile deviation ──
base3 = datetime(2024, 3, 1)

# Normal baseline period (small transactions for 3 months)
for i in range(12):
    add(base3 + timedelta(days=i*7), 250 + i*50, 'Ahmed Al-Rashid', 'Grocery Store', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Weekly groceries', 'Purchase', 'BCN-003')

# Watchlist match (Rule 4): sender/receiver name close to watchlist entry
add(base3 + timedelta(days=90), 7500, 'Ahmed Al-Rashid', 'Volkov Enterprises LLC', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Business deal', 'Transfer', 'BCN-003')
add(base3 + timedelta(days=92), 3000, 'Dimitri Volkov Trading', 'Ahmed Al-Rashid', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Return payment', 'Transfer', 'BCN-003')

# Counterparty concentration - Fan-in (Rule 8): many senders in short window
for i in range(8):
    add(base3 + timedelta(days=100 + i), 3000 + i*500, f'Sender_{chr(65+i)} Corp', 'Ahmed Al-Rashid', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Payment from {chr(65+i)}', 'Credit', 'BCN-003')
# Then one big outgoing
add(base3 + timedelta(days=110), 30000, 'Ahmed Al-Rashid', 'Foreign Account', 'AE070331234567890123456', 'ABORAEAO', 'EUR', 'Large outgoing', 'Debit', 'BCN-003')

# Profile deviation (Rule 9): after small txns, suddenly huge ones
add(base3 + timedelta(days=120), 50000, 'Ahmed Al-Rashid', 'Luxury Cars BV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Vehicle purchase', 'Purchase', 'BCN-003')
add(base3 + timedelta(days=122), 35000, 'Unknown Source', 'Ahmed Al-Rashid', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', 'Cash deposit', 'Deposit', 'BCN-003')


# ── BCN-004: "Sophie Mueller" — triggers dormant account ──
base4 = datetime(2023, 6, 1)

# A few old transactions
add(base4, 1500, 'Sophie Mueller', 'Rent Payment', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'June rent', 'Transfer', 'BCN-004')
add(base4 + timedelta(days=15), 800, 'Sophie Mueller', 'Utilities', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'Electricity', 'Transfer', 'BCN-004')

# 120-day gap (dormant)

# Dormant reactivation (Rule 7): burst after long silence
dormant_resume = base4 + timedelta(days=150)
add(dormant_resume, 12000, 'Reactivation Source', 'Sophie Mueller', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'Large deposit', 'Credit', 'BCN-004')
add(dormant_resume + timedelta(days=1), 8000, 'Sophie Mueller', 'Crypto Exchange', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'Crypto purchase', 'Transfer', 'BCN-004')
add(dormant_resume + timedelta(days=2), 5000, 'Sophie Mueller', 'Cash Withdrawal', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'ATM withdrawal', 'Withdrawal', 'BCN-004')
add(dormant_resume + timedelta(days=3), 9500, 'Sophie Mueller', 'Foreign Transfer', 'TR330006100519786457841326', 'AKBNTR33', 'EUR', 'Transfer to Turkey', 'International Transfer', 'BCN-004')
add(dormant_resume + timedelta(days=5), 7000, 'Sophie Mueller', 'Gold Dealer', 'DE89370400440532013000', 'COBADEFF', 'EUR', 'Gold purchase', 'Purchase', 'BCN-004')


# ── BCN-005: "Clean Customer BV" — a clean customer with no flags ──
base5 = datetime(2024, 1, 1)
for i in range(20):
    amt = 1500 + (i % 5) * 300 + (i * 17 % 100)
    add(base5 + timedelta(days=i*14), amt, 'Clean Customer BV', 'Regular Supplier NL', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Regular payment {i+1}', 'Transfer', 'BCN-005')
for i in range(10):
    add(base5 + timedelta(days=7 + i*28), 2200 + i*50, 'Client Revenue', 'Clean Customer BV', 'NL91ABNA0417164300', 'ABNANL2A', 'EUR', f'Client invoice {i+1}', 'Credit', 'BCN-005')


transactions_df = pd.DataFrame(rows)
transactions_df.to_excel(os.path.join(OUTPUT_DIR, 'transactions.xlsx'), index=False)
print(f"Created transactions.xlsx with {len(rows)} rows")


# ── Watchlist ─────────────────────────────────────────────────────────────────
watchlist = pd.DataFrame([
    {'Name': 'Volkov Enterprises', 'Type': 'Organization', 'Notes': 'Suspected shell company linked to sanctions evasion'},
    {'Name': 'Dimitri Volkov', 'Type': 'Person', 'Notes': 'PEP - Former government official under investigation'},
    {'Name': 'Tehran Import Company', 'Type': 'Organization', 'Notes': 'Listed entity - sanctioned trade'},
    {'Name': 'Al-Qaeda Finance Network', 'Type': 'Organization', 'Notes': 'Terrorist financing'},
    {'Name': 'Caribbean Holdings Ltd', 'Type': 'Organization', 'Notes': 'Known shell company in British Virgin Islands'},
    {'Name': 'Offshore Investments Ltd', 'Type': 'Organization', 'Notes': 'Suspected money laundering vehicle'},
    {'Name': 'Golden Dragon Trading', 'Type': 'Organization', 'Notes': 'Trade-based ML suspect'},
    {'Name': 'Ivan Petrov', 'Type': 'Person', 'Notes': 'Sanctions list - oligarch'},
    {'Name': 'Maria Sokolov', 'Type': 'Person', 'Notes': 'PEP associate'},
    {'Name': 'Hassan Ali Ibrahim', 'Type': 'Person', 'Notes': 'OFAC SDN list'},
])
watchlist.to_excel(os.path.join(OUTPUT_DIR, 'watchlist.xlsx'), index=False)
print(f"Created watchlist.xlsx with {len(watchlist)} entries")


# ── High-Risk Countries ──────────────────────────────────────────────────────
countries = pd.DataFrame([
    {'Country Name': 'Iran', 'Country Code': 'IR', 'Risk Level': 'Blacklist'},
    {'Country Name': 'North Korea', 'Country Code': 'KP', 'Risk Level': 'Blacklist'},
    {'Country Name': 'Syria', 'Country Code': 'SY', 'Risk Level': 'Blacklist'},
    {'Country Name': 'Myanmar', 'Country Code': 'MM', 'Risk Level': 'Blacklist'},
    {'Country Name': 'Afghanistan', 'Country Code': 'AF', 'Risk Level': 'Blacklist'},
    {'Country Name': 'Turkey', 'Country Code': 'TR', 'Risk Level': 'Greylist'},
    {'Country Name': 'South Africa', 'Country Code': 'ZA', 'Risk Level': 'Greylist'},
    {'Country Name': 'United Arab Emirates', 'Country Code': 'AE', 'Risk Level': 'Greylist'},
    {'Country Name': 'Nigeria', 'Country Code': 'NG', 'Risk Level': 'Greylist'},
    {'Country Name': 'Pakistan', 'Country Code': 'PK', 'Risk Level': 'Greylist'},
    {'Country Name': 'Belarus', 'Country Code': 'BY', 'Risk Level': 'Greylist'},
    {'Country Name': 'Panama', 'Country Code': 'PA', 'Risk Level': 'Greylist'},
])
countries.to_excel(os.path.join(OUTPUT_DIR, 'high_risk_countries.xlsx'), index=False)
print(f"Created high_risk_countries.xlsx with {len(countries)} countries")


# ── Work Instructions ────────────────────────────────────────────────────────
instructions = pd.DataFrame([
    {'Step': 1, 'Category': 'Initial Review', 'Instruction': 'Verify customer identity and Business Contact Number against internal records'},
    {'Step': 2, 'Category': 'Initial Review', 'Instruction': 'Check customer risk classification (CDD/EDD status) in the core banking system'},
    {'Step': 3, 'Category': 'Transaction Analysis', 'Instruction': 'Review all transactions exceeding EUR 10,000 for proper documentation'},
    {'Step': 4, 'Category': 'Transaction Analysis', 'Instruction': 'Identify any structuring patterns (multiple transactions just below reporting thresholds)'},
    {'Step': 5, 'Category': 'Transaction Analysis', 'Instruction': 'Check for rapid fund movements (funds received and sent within 48 hours)'},
    {'Step': 6, 'Category': 'Geographic Risk', 'Instruction': 'Flag transactions involving FATF blacklist or greylist countries'},
    {'Step': 7, 'Category': 'Geographic Risk', 'Instruction': 'Verify business justification for any cross-border transactions to high-risk jurisdictions'},
    {'Step': 8, 'Category': 'Watchlist Screening', 'Instruction': 'Run sender/receiver names against internal and external watchlists (PEP, sanctions, adverse media)'},
    {'Step': 9, 'Category': 'Watchlist Screening', 'Instruction': 'Investigate any fuzzy matches with confidence above 70%'},
    {'Step': 10, 'Category': 'Pattern Detection', 'Instruction': 'Check for round-amount transaction patterns that may indicate trade-based ML'},
    {'Step': 11, 'Category': 'Pattern Detection', 'Instruction': 'Look for dormant account reactivation followed by unusual transaction activity'},
    {'Step': 12, 'Category': 'Escalation', 'Instruction': 'If overall risk score exceeds 50 (HIGH), escalate to the AML compliance officer'},
    {'Step': 13, 'Category': 'Escalation', 'Instruction': 'File Suspicious Transaction Report (STR) if warranted under EU 6AMLD Article 33'},
    {'Step': 14, 'Category': 'Documentation', 'Instruction': 'Document all findings and rationale in the case management system'},
])
instructions.to_excel(os.path.join(OUTPUT_DIR, 'work_instructions.xlsx'), index=False)
print(f"Created work_instructions.xlsx with {len(instructions)} instructions")

print("\nAll sample data files created successfully in:", os.path.abspath(OUTPUT_DIR))
