import { RISK_LEVEL_COLORS, COLORS } from "./constants";

/**
 * Format a monetary value with thousands separators and 2 decimals.
 * Defaults to EUR if no currency is provided.
 */
export function formatCurrency(
  amount: number,
  currency: string = "EUR"
): string {
  return new Intl.NumberFormat("en-EU", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format an ISO date string to a human-readable locale string.
 */
export function formatDate(date: string): string {
  if (!date) return "-";
  const d = new Date(date);
  if (isNaN(d.getTime())) return date;
  return d.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

/**
 * Return the hex colour for a given risk level string.
 */
export function getRiskColor(level: string): string {
  return RISK_LEVEL_COLORS[level?.toUpperCase()] ?? COLORS.abnGrey;
}

/**
 * Return a translucent background colour for risk level badges.
 */
export function getRiskBgColor(level: string): string {
  const map: Record<string, string> = {
    LOW: "bg-risk-low/15",
    MEDIUM: "bg-risk-medium/15",
    HIGH: "bg-risk-high/15",
    CRITICAL: "bg-risk-critical/15",
  };
  return map[level?.toUpperCase()] ?? "bg-gray-100";
}
