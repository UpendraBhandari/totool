"use client";

import { use } from "react";
import Link from "next/link";
import { useCustomerData } from "@/hooks/useCustomerData";
import Spinner from "@/components/ui/Spinner";
import Alert from "@/components/ui/Alert";
import CustomerHeader from "@/components/dashboard/CustomerHeader";
import RiskScore from "@/components/dashboard/RiskScore";
import SuspiciousFlags from "@/components/dashboard/SuspiciousFlags";
import TransactionTimeline from "@/components/dashboard/TransactionTimeline";
import TransactionTable from "@/components/dashboard/TransactionTable";
import PatternAnalysis from "@/components/dashboard/PatternAnalysis";
import WatchlistMatches from "@/components/dashboard/WatchlistMatches";
import WorkInstructions from "@/components/dashboard/WorkInstructions";

interface PageProps {
  params: Promise<{ bcn: string }>;
}

export default function CustomerPage({ params }: PageProps) {
  const { bcn } = use(params);
  const { data, loading, error } = useCustomerData(bcn);

  /* ---- Loading ---- */
  if (loading) {
    return (
      <div className="flex min-h-[calc(100vh-128px)] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Spinner size="lg" />
          <p className="text-sm text-abn-grey">Loading customer data...</p>
        </div>
      </div>
    );
  }

  /* ---- Error ---- */
  if (error || !data) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <Alert type="error" title="Failed to load customer data">
          {error || "Customer data is unavailable. Please try again."}
        </Alert>
        <Link
          href="/"
          className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-abn-teal hover:text-abn-teal-dark"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
            />
          </svg>
          Back to Search
        </Link>
      </div>
    );
  }

  /* ---- Success ---- */
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Back link */}
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-abn-teal hover:text-abn-teal-dark"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
          />
        </svg>
        Back to Search
      </Link>

      <div className="space-y-6">
        {/* Row 1: Customer header + Risk score */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <CustomerHeader customer={data} />
          </div>
          <div>
            <RiskScore assessment={data.risk_assessment} />
          </div>
        </div>

        {/* Row 2: Suspicious flags */}
        <SuspiciousFlags alerts={data.alerts} />

        {/* Row 3: Timeline + Pattern Analysis */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <TransactionTimeline
              transactions={data.transactions}
              alerts={data.alerts}
            />
          </div>
          <div>
            <PatternAnalysis patterns={data.patterns} />
          </div>
        </div>

        {/* Row 4: Transaction table */}
        <TransactionTable transactions={data.transactions} />

        {/* Row 5: Watchlist + Work instructions */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <WatchlistMatches matches={data.watchlist_matches} />
          <WorkInstructions instructions={data.work_instructions} />
        </div>
      </div>
    </div>
  );
}
