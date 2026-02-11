/* ------------------------------------------------------------------ */
/*  TypeScript interfaces matching backend Pydantic schemas            */
/* ------------------------------------------------------------------ */

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type AlertSeverity = "LOW" | "MEDIUM" | "HIGH";

export type AlertType =
  | "STRUCTURING"
  | "THRESHOLD"
  | "HIGH_RISK_COUNTRY"
  | "WATCHLIST_MATCH"
  | "RAPID_MOVEMENT"
  | "ROUND_AMOUNT"
  | "DORMANT_ACCOUNT"
  | "COUNTERPARTY_CONCENTRATION"
  | "PROFILE_DEVIATION"
  | "FLOW_THROUGH";

/* ---- Transaction ---- */

export interface Transaction {
  index: number;
  date: string;
  amount: number;
  sender: string;
  receiver: string;
  iban: string | null;
  bic: string | null;
  currency: string;
  description: string | null;
  transaction_type: string | null;
  flags: string[];
}

/* ---- Alert ---- */

export interface Alert {
  id: string;
  rule_name: string;
  severity: AlertSeverity;
  description: string;
  affected_transaction_indices: number[];
  alert_type: AlertType;
}

/* ---- Risk ---- */

export interface ContributingFactor {
  factor: string;
  weight: number;
}

export interface RiskAssessment {
  overall_score: number;
  risk_level: RiskLevel;
  contributing_factors: string[];
}

/* ---- Watchlist ---- */

export interface WatchlistMatch {
  matched_entity: string;
  watchlist_entry: string;
  match_score: number;
  match_field: string;
  transaction_indices: number[];
}

/* ---- Patterns ---- */

export interface MonthlyData {
  month: string;
  volume: number;
}

export interface TypeData {
  type: string;
  value: number;
}

export interface CurrencyData {
  currency: string;
  value: number;
}

export interface PatternData {
  by_month: Record<string, number>;
  by_type: Record<string, number>;
  by_currency: Record<string, number>;
  round_amount_ratio: number;
  avg_transaction_size: number;
  high_risk_country_exposure: number;
}

/* ---- Customer Overview ---- */

export interface CustomerOverview {
  business_contact_number: string;
  customer_name: string | null;
  risk_assessment: RiskAssessment;
  transactions: Transaction[];
  alerts: Alert[];
  patterns: PatternData;
  watchlist_matches: WatchlistMatch[];
  work_instructions: string[];
}

/* ---- Upload ---- */

export interface UploadResponse {
  status: string;
  record_count: number;
  warnings: string[];
}

export interface UploadStatus {
  transactions: boolean;
  watchlist: boolean;
  high_risk_countries: boolean;
  work_instructions: boolean;
}

/* ---- Search ---- */

export interface SearchResult {
  bcn: string;
  name: string;
  transaction_count: number;
}

/* ---- Work instruction ---- */

export interface WorkInstruction {
  business_contact_number: string;
  instruction: string;
  category?: string;
}
