"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import SearchBar from "@/components/search/SearchBar";
import UploadStatusComponent from "@/components/upload/UploadStatus";
import { getUploadStatus } from "@/lib/api";
import type { UploadStatus } from "@/lib/types";

export default function Home() {
  const [status, setStatus] = useState<UploadStatus>({
    transactions: false,
    watchlist: false,
    high_risk_countries: false,
    work_instructions: false,
  });
  const [statusLoaded, setStatusLoaded] = useState(false);

  useEffect(() => {
    getUploadStatus()
      .then((s) => {
        setStatus(s);
        setStatusLoaded(true);
      })
      .catch(() => {
        setStatusLoaded(true);
      });
  }, []);

  const hasData =
    status.transactions ||
    status.watchlist ||
    status.high_risk_countries ||
    status.work_instructions;

  return (
    <div className="flex min-h-[calc(100vh-128px)] flex-col items-center justify-center px-4">
      {/* Title */}
      <h1 className="mb-2 text-4xl font-bold tracking-tight text-abn-teal sm:text-5xl">
        Transaction Monitor
      </h1>
      <p className="mb-8 max-w-lg text-center text-sm text-abn-grey">
        Search a customer by Business Contact Number to begin investigation
      </p>

      {/* Search bar */}
      <SearchBar />

      {/* Upload status & link */}
      <div className="mt-10 flex flex-col items-center gap-4">
        {statusLoaded && (
          <>
            <UploadStatusComponent status={status} />
            {!hasData && (
              <p className="text-xs text-abn-grey-light">
                Upload transaction data to begin
              </p>
            )}
          </>
        )}

        <Link
          href="/upload"
          className="inline-flex items-center gap-2 rounded-md bg-abn-teal px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-abn-teal-dark"
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
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          Upload Data
        </Link>
      </div>
    </div>
  );
}
