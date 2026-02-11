"use client";

import type { UploadStatus as UploadStatusType } from "@/lib/types";

interface UploadStatusProps {
  status: UploadStatusType;
}

const fileLabels: { key: keyof UploadStatusType; label: string }[] = [
  { key: "transactions", label: "Transactions" },
  { key: "watchlist", label: "Watchlist" },
  { key: "high_risk_countries", label: "High-Risk Countries" },
  { key: "work_instructions", label: "Work Instructions" },
];

export default function UploadStatus({ status }: UploadStatusProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {fileLabels.map(({ key, label }) => {
        const uploaded = status[key];
        return (
          <div
            key={key}
            className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
              uploaded
                ? "border-risk-low/30 bg-green-50 text-green-800"
                : "border-gray-200 bg-gray-50 text-abn-grey"
            }`}
          >
            {uploaded ? (
              <svg
                className="h-3.5 w-3.5 text-risk-low"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="h-3.5 w-3.5 text-abn-grey-light"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            {label}
          </div>
        );
      })}
    </div>
  );
}
