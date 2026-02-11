"use client";

import { useState, useCallback, useEffect } from "react";
import {
  uploadFile as apiUpload,
  getUploadStatus as apiStatus,
  clearData as apiClear,
} from "@/lib/api";
import type { UploadStatus, UploadResponse } from "@/lib/types";

interface UploadState {
  status: UploadStatus;
  loading: boolean;
  error: string | null;
  fileResults: Record<string, { filename: string; recordCount: number } | null>;
}

export function useUpload() {
  const [state, setState] = useState<UploadState>({
    status: {
      transactions: false,
      watchlist: false,
      high_risk_countries: false,
      work_instructions: false,
    },
    loading: false,
    error: null,
    fileResults: {
      transactions: null,
      watchlist: null,
      high_risk_countries: null,
      work_instructions: null,
    },
  });

  const refreshStatus = useCallback(async () => {
    try {
      const status = await apiStatus();
      setState((prev) => ({ ...prev, status }));
    } catch {
      // Silently ignore – status endpoint may not yet be available
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  const upload = useCallback(
    async (
      type: string,
      file: File
    ): Promise<UploadResponse> => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const result = await apiUpload(type, file);
        setState((prev) => ({
          ...prev,
          loading: false,
          status: { ...prev.status, [type]: true },
          fileResults: {
            ...prev.fileResults,
            [type]: {
              filename: file.name,
              recordCount: result.record_count,
            },
          },
        }));
        return result;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Upload failed";
        setState((prev) => ({
          ...prev,
          loading: false,
          error: message,
        }));
        throw err;
      }
    },
    []
  );

  const clear = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      await apiClear();
      setState({
        status: {
          transactions: false,
          watchlist: false,
          high_risk_countries: false,
          work_instructions: false,
        },
        loading: false,
        error: null,
        fileResults: {
          transactions: null,
          watchlist: null,
          high_risk_countries: null,
          work_instructions: null,
        },
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Clear failed";
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
      }));
    }
  }, []);

  return {
    status: state.status,
    loading: state.loading,
    error: state.error,
    fileResults: state.fileResults,
    upload,
    clear,
    refreshStatus,
  };
}
