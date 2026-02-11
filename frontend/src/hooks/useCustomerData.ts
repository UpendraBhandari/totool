"use client";

import { useState, useEffect } from "react";
import { getCustomerOverview } from "@/lib/api";
import type { CustomerOverview } from "@/lib/types";

interface CustomerDataState {
  data: CustomerOverview | null;
  loading: boolean;
  error: string | null;
}

export function useCustomerData(bcn: string) {
  const [state, setState] = useState<CustomerDataState>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    if (!bcn) {
      setState({ data: null, loading: false, error: "No BCN provided" });
      return;
    }

    let cancelled = false;

    async function fetchData() {
      setState({ data: null, loading: true, error: null });
      try {
        const overview = await getCustomerOverview(bcn);
        if (!cancelled) {
          setState({ data: overview, loading: false, error: null });
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof Error ? err.message : "Failed to load customer data";
          setState({ data: null, loading: false, error: message });
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [bcn]);

  return state;
}
