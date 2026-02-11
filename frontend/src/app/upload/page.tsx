"use client";

import Link from "next/link";
import FileUploader from "@/components/upload/FileUploader";
import { useUpload } from "@/hooks/useUpload";
import { FILE_TYPES } from "@/lib/constants";
import Alert from "@/components/ui/Alert";

export default function UploadPage() {
  const { upload, clear, loading, error } = useUpload();

  const fileTypes = [
    FILE_TYPES.transactions,
    FILE_TYPES.watchlist,
    FILE_TYPES.high_risk_countries,
    FILE_TYPES.work_instructions,
  ];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
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

      {/* Title */}
      <h1 className="text-2xl font-bold text-gray-900">Upload Data Files</h1>
      <p className="mt-1 mb-6 text-sm text-abn-grey">
        Upload the required Excel files to populate the AML monitoring system.
        All files must be in .xlsx or .xls format.
      </p>

      {/* Error alert */}
      {error && (
        <Alert type="error" className="mb-6">
          {error}
        </Alert>
      )}

      {/* File uploaders in 2x2 grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {fileTypes.map((ft) => (
          <FileUploader
            key={ft.key}
            fileType={ft.key}
            label={ft.label}
            description={ft.description}
            required={ft.required}
            onUpload={upload}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="mt-8 flex items-center justify-between">
        <Link
          href="/"
          className="text-sm font-medium text-abn-teal hover:text-abn-teal-dark"
        >
          Back to Search
        </Link>
        <button
          type="button"
          onClick={clear}
          disabled={loading}
          className="rounded-md border border-risk-critical/30 bg-white px-4 py-2 text-sm font-medium text-risk-critical transition-colors hover:bg-flag-bg disabled:cursor-not-allowed disabled:opacity-50"
        >
          Clear All Data
        </button>
      </div>
    </div>
  );
}
