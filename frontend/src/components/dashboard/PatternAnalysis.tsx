"use client";

import { useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import type { PatternData } from "@/lib/types";
import { COLORS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";
import Card from "@/components/ui/Card";

interface PatternAnalysisProps {
  patterns: PatternData;
}

const PIE_COLORS = [
  COLORS.abnTeal,
  COLORS.abnYellow,
  COLORS.riskHigh,
  COLORS.abnTealDark,
  COLORS.abnGreyDark,
  COLORS.riskLow,
  COLORS.riskCritical,
  COLORS.abnGreyLight,
];

export default function PatternAnalysis({ patterns }: PatternAnalysisProps) {
  /* ---- Monthly data for bar chart ---- */
  const monthlyData = useMemo(() => {
    return Object.entries(patterns.by_month)
      .map(([month, volume]) => ({ month, volume }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [patterns.by_month]);

  /* ---- Type data for pie chart ---- */
  const typeData = useMemo(() => {
    return Object.entries(patterns.by_type).map(([type, value]) => ({
      name: type || "Unknown",
      value,
    }));
  }, [patterns.by_type]);

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900">Pattern Analysis</h3>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Monthly volume bar chart */}
        <Card className="p-4">
          <p className="mb-3 text-xs font-medium uppercase tracking-wider text-abn-grey">
            Monthly Transaction Volume
          </p>
          <div className="h-56 w-full">
            {monthlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={monthlyData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="month"
                    tick={{ fontSize: 10, fill: COLORS.abnGrey }}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: COLORS.abnGrey }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v: number) =>
                      v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v)
                    }
                  />
                  <RechartsTooltip
                    content={({ active, payload }) => {
                      if (!active || !payload?.[0]) return null;
                      const d = payload[0].payload as {
                        month: string;
                        volume: number;
                      };
                      return (
                        <div className="rounded border border-gray-200 bg-white px-3 py-2 shadow">
                          <p className="text-xs font-semibold">{d.month}</p>
                          <p className="text-xs text-abn-grey-dark">
                            {formatCurrency(d.volume)}
                          </p>
                        </div>
                      );
                    }}
                  />
                  <Bar
                    dataKey="volume"
                    fill={COLORS.abnTeal}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-abn-grey">
                No monthly data available
              </div>
            )}
          </div>
        </Card>

        {/* Transaction type pie chart */}
        <Card className="p-4">
          <p className="mb-3 text-xs font-medium uppercase tracking-wider text-abn-grey">
            Transaction Type Distribution
          </p>
          <div className="h-56 w-full">
            {typeData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={typeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    dataKey="value"
                    nameKey="name"
                    paddingAngle={2}
                  >
                    {typeData.map((_, idx) => (
                      <Cell
                        key={idx}
                        fill={PIE_COLORS[idx % PIE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    content={({ active, payload }) => {
                      if (!active || !payload?.[0]) return null;
                      const d = payload[0].payload as {
                        name: string;
                        value: number;
                      };
                      return (
                        <div className="rounded border border-gray-200 bg-white px-3 py-2 shadow">
                          <p className="text-xs font-semibold">{d.name}</p>
                          <p className="text-xs text-abn-grey-dark">
                            {formatCurrency(d.value)}
                          </p>
                        </div>
                      );
                    }}
                  />
                  <Legend
                    iconType="circle"
                    iconSize={8}
                    wrapperStyle={{ fontSize: 11 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-abn-grey">
                No type data available
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Avg Transaction Size"
          value={formatCurrency(patterns.avg_transaction_size)}
        />
        <StatCard
          label="Round Amount Ratio"
          value={`${(patterns.round_amount_ratio * 100).toFixed(1)}%`}
          highlight={patterns.round_amount_ratio > 0.5}
        />
        <StatCard
          label="High-Risk Country Exposure"
          value={`${(patterns.high_risk_country_exposure * 100).toFixed(1)}%`}
          highlight={patterns.high_risk_country_exposure > 0.1}
        />
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        highlight
          ? "border-risk-high/30 bg-orange-50"
          : "border-gray-200 bg-white"
      }`}
    >
      <p className="text-[10px] font-medium uppercase tracking-wider text-abn-grey">
        {label}
      </p>
      <p
        className={`mt-1 text-lg font-bold ${
          highlight ? "text-risk-high" : "text-gray-900"
        }`}
      >
        {value}
      </p>
    </div>
  );
}
