import type { Alert } from "@/lib/types";
import Badge from "@/components/ui/Badge";

interface SuspiciousFlagsProps {
  alerts: Alert[];
}

const severityOrder: Record<string, number> = {
  HIGH: 0,
  MEDIUM: 1,
  LOW: 2,
};

const severityVariant: Record<string, "danger" | "warning" | "success"> = {
  HIGH: "danger",
  MEDIUM: "warning",
  LOW: "success",
};

const severityBorder: Record<string, string> = {
  HIGH: "border-l-risk-critical",
  MEDIUM: "border-l-risk-medium",
  LOW: "border-l-risk-low",
};

export default function SuspiciousFlags({ alerts }: SuspiciousFlagsProps) {
  if (alerts.length === 0) {
    return (
      <div className="rounded-lg border border-risk-low/30 bg-green-50 p-6">
        <div className="flex items-center gap-3">
          <svg
            className="h-6 w-6 text-risk-low"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          <p className="text-sm font-medium text-green-800">
            No suspicious activity detected
          </p>
        </div>
      </div>
    );
  }

  const sorted = [...alerts].sort(
    (a, b) =>
      (severityOrder[a.severity] ?? 3) - (severityOrder[b.severity] ?? 3)
  );

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-900">
        Suspicious Activity Alerts ({alerts.length})
      </h3>
      {sorted.map((alert) => (
        <div
          key={alert.id}
          className={`rounded-lg border border-gray-200 border-l-4 bg-white p-4 shadow-sm ${
            severityBorder[alert.severity] ?? "border-l-gray-300"
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="text-sm font-bold text-gray-900">
                  {alert.rule_name}
                </p>
                <Badge variant={severityVariant[alert.severity] ?? "default"}>
                  {alert.severity}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-abn-grey-dark">
                {alert.description}
              </p>
            </div>
            {alert.affected_transaction_indices.length > 0 && (
              <Badge variant="info" className="shrink-0">
                Affects {alert.affected_transaction_indices.length} transaction
                {alert.affected_transaction_indices.length !== 1 ? "s" : ""}
              </Badge>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
