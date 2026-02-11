export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const COLORS = {
  abnTeal: "#009488",
  abnTealDark: "#007D73",
  abnTealLight: "#E0F5F3",
  abnYellow: "#F9BD20",
  abnYellowLight: "#FCD97A",
  abnGrey: "#878787",
  abnGreyLight: "#B0B0B0",
  abnGreyDark: "#5A5A5A",
  riskLow: "#4CAF50",
  riskMedium: "#F9BD20",
  riskHigh: "#FF9800",
  riskCritical: "#F44336",
  flagBg: "#FEF2F2",
  flagBorder: "#FECACA",
} as const;

export const RISK_LEVEL_COLORS: Record<string, string> = {
  LOW: COLORS.riskLow,
  MEDIUM: COLORS.riskMedium,
  HIGH: COLORS.riskHigh,
  CRITICAL: COLORS.riskCritical,
};

export const FILE_TYPES = {
  transactions: {
    key: "transactions",
    label: "Transaction Data",
    description: "Upload customer transaction records in Excel format.",
    required: true,
  },
  watchlist: {
    key: "watchlist",
    label: "Suspicious Persons / Organizations Watchlist",
    description:
      "Upload the sanctions and watchlist data for screening against transactions.",
    required: true,
  },
  high_risk_countries: {
    key: "high-risk-countries",
    label: "High-Risk Countries",
    description:
      "Upload the list of high-risk countries with their risk classifications.",
    required: true,
  },
  work_instructions: {
    key: "work-instructions",
    label: "Work Instructions",
    description:
      "Upload any existing work instructions associated with customers.",
    required: false,
  },
} as const;
