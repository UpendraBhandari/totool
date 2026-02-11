"use client";

import { getRiskColor } from "@/lib/utils";
import type { RiskAssessment } from "@/lib/types";

interface RiskScoreProps {
  assessment: RiskAssessment;
}

export default function RiskScore({ assessment }: RiskScoreProps) {
  const { overall_score, risk_level, contributing_factors } = assessment;
  const color = getRiskColor(risk_level);

  // SVG circular gauge parameters
  const size = 160;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (overall_score / 100) * circumference;
  const offset = circumference - progress;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">
        Risk Assessment
      </h3>

      {/* Circular gauge */}
      <div className="flex justify-center">
        <div className="relative" style={{ width: size, height: size }}>
          <svg width={size} height={size} className="-rotate-90">
            {/* Background circle */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth={strokeWidth}
            />
            {/* Progress arc */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-700 ease-out"
            />
          </svg>
          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span
              className="text-3xl font-bold"
              style={{ color }}
            >
              {Math.round(overall_score)}
            </span>
            <span
              className="text-xs font-semibold uppercase tracking-wider"
              style={{ color }}
            >
              {risk_level}
            </span>
          </div>
        </div>
      </div>

      {/* Contributing factors */}
      {contributing_factors.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-abn-grey">
            Contributing Factors
          </p>
          <ul className="space-y-1.5">
            {contributing_factors.map((factor, idx) => (
              <li
                key={idx}
                className="flex items-center gap-2 text-sm text-gray-700"
              >
                <span
                  className="h-1.5 w-1.5 shrink-0 rounded-full"
                  style={{ backgroundColor: color }}
                />
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
