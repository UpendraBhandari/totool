"use client";

import { useState, useRef, useCallback } from "react";
import Spinner from "@/components/ui/Spinner";

interface FileUploaderProps {
  fileType: string;
  label: string;
  description: string;
  required: boolean;
  onUpload: (type: string, file: File) => Promise<{ record_count: number }>;
}

type UploadState = "idle" | "uploading" | "success" | "error";

export default function FileUploader({
  fileType,
  label,
  description,
  required,
  onUpload,
}: FileUploaderProps) {
  const [state, setState] = useState<UploadState>("idle");
  const [filename, setFilename] = useState<string | null>(null);
  const [recordCount, setRecordCount] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File) => {
      setState("uploading");
      setFilename(file.name);
      setErrorMessage(null);
      try {
        const result = await onUpload(fileType, file);
        setRecordCount(result.record_count);
        setState("success");
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Upload failed";
        setErrorMessage(msg);
        setState("error");
      }
    },
    [fileType, onUpload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const reset = () => {
    setState("idle");
    setFilename(null);
    setRecordCount(0);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      {/* Header */}
      <div className="mb-3 flex items-center gap-2">
        <h3 className="text-sm font-semibold text-gray-900">{label}</h3>
        {required ? (
          <span className="rounded bg-risk-critical/10 px-1.5 py-0.5 text-[10px] font-bold uppercase text-risk-critical">
            Required
          </span>
        ) : (
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-bold uppercase text-abn-grey">
            Optional
          </span>
        )}
      </div>
      <p className="mb-4 text-xs text-abn-grey">{description}</p>

      {/* Drop zone */}
      {state === "idle" && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
            isDragging
              ? "border-abn-teal bg-abn-teal-light"
              : "border-gray-300 hover:border-abn-teal hover:bg-abn-teal-light/50"
          }`}
        >
          {/* File icon */}
          <svg
            className="h-8 w-8 text-abn-grey-light"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
          <p className="text-sm font-medium text-gray-600">
            Drag &amp; drop or click to browse
          </p>
          <p className="text-xs text-abn-grey-light">
            Accepts .xlsx, .xls files
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleInputChange}
            className="hidden"
          />
        </div>
      )}

      {/* Uploading state */}
      {state === "uploading" && (
        <div className="flex flex-col items-center gap-2 rounded-lg border-2 border-dashed border-abn-teal bg-abn-teal-light p-6">
          <Spinner size="md" />
          <p className="text-sm text-abn-teal-dark">Uploading {filename}...</p>
        </div>
      )}

      {/* Success state */}
      {state === "success" && (
        <div className="rounded-lg border border-risk-low/30 bg-green-50 p-4">
          <div className="flex items-center gap-3">
            <svg
              className="h-8 w-8 text-risk-low"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <p className="text-sm font-semibold text-green-800">{filename}</p>
              <p className="text-xs text-green-600">
                {recordCount} record{recordCount !== 1 ? "s" : ""} loaded
                successfully
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={reset}
            className="mt-3 text-xs font-medium text-abn-grey hover:text-risk-critical"
          >
            Remove
          </button>
        </div>
      )}

      {/* Error state */}
      {state === "error" && (
        <div className="rounded-lg border border-risk-critical/30 bg-flag-bg p-4">
          <div className="flex items-center gap-3">
            <svg
              className="h-8 w-8 text-risk-critical"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <p className="text-sm font-semibold text-red-800">Upload failed</p>
              <p className="text-xs text-red-600">
                {errorMessage || "An unknown error occurred"}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={reset}
            className="mt-3 text-xs font-medium text-abn-grey hover:text-abn-teal"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  );
}
