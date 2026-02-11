"use client";

import { useMemo } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import type { Transaction, Alert } from "@/lib/types";
import { COLORS } from "@/lib/constants";
import { formatCurrency, formatDate } from "@/lib/utils";

interface TransactionTimelineProps {
  transactions: Transaction[];
  alerts: Alert[];
}

interface ChartPoint {
  date: string;
  dateLabel: string;
  amount: number;
  flagged: number | null;
  flags: string[];
}

export default function TransactionTimeline({
  transactions,
  alerts,
}: TransactionTimelineProps) {
  const data = useMemo<ChartPoint[]>(() => {
    // Build a set of flagged transaction indices
    const flaggedIndices = new Set<number>();
    alerts.forEach((a) =>
      a.affected_transaction_indices.forEach((i) => flaggedIndices.add(i))
    );

    // Sort transactions by date
    const sorted = [...transactions].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    return sorted.map((t) => {
      const isFlagged =
        flaggedIndices.has(t.index) || (t.flags && t.flags.length > 0);
      return {
        date: t.date,
        dateLabel: formatDate(t.date),
        amount: t.amount,
        flagged: isFlagged ? t.amount : null,
        flags: t.flags ?? [],
      };
    });
  }, [transactions, alerts]);

  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg border border-gray-200 bg-white text-sm text-abn-grey">
        No transaction data available
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">
        Transaction Timeline
      </h3>
      <div className="h-96 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={data}
            margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="dateLabel"
              tick={{ fontSize: 11, fill: COLORS.abnGrey }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11, fill: COLORS.abnGrey }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) =>
                v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v)
              }
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null;
                const d = payload[0].payload as ChartPoint;
                return (
                  <div className="rounded-lg border border-gray-200 bg-white px-3 py-2 shadow-lg">
                    <p className="text-xs font-semibold text-gray-900">
                      {d.dateLabel}
                    </p>
                    <p className="text-xs text-abn-grey-dark">
                      {formatCurrency(d.amount)}
                    </p>
                    {d.flags.length > 0 && (
                      <p className="mt-1 text-xs font-medium text-risk-critical">
                        Flags: {d.flags.join(", ")}
                      </p>
                    )}
                  </div>
                );
              }}
            />
            <Area
              type="monotone"
              dataKey="amount"
              stroke={COLORS.abnTeal}
              fill={COLORS.abnTeal}
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Scatter
              dataKey="flagged"
              fill={COLORS.riskCritical}
              r={5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
