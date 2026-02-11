"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { searchCustomer } from "@/lib/api";
import type { SearchResult } from "@/lib/types";
import Spinner from "@/components/ui/Spinner";

export default function SearchBar() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [hasSearched, setHasSearched] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /* ---- Debounced search ---- */
  const doSearch = useCallback(async (q: string) => {
    if (q.trim().length === 0) {
      setResults([]);
      setHasSearched(false);
      setIsOpen(false);
      return;
    }

    setLoading(true);
    setHasSearched(true);
    try {
      const data = await searchCustomer(q.trim());
      setResults(data);
      setIsOpen(true);
      setActiveIndex(-1);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (value: string) => {
    setQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(value), 300);
  };

  /* ---- Select result ---- */
  const selectResult = (result: SearchResult) => {
    setQuery(result.bcn);
    setIsOpen(false);
    router.push(`/customer/${encodeURIComponent(result.bcn)}`);
  };

  /* ---- Keyboard navigation ---- */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < results.length) {
          selectResult(results[activeIndex]);
        }
        break;
      case "Escape":
        setIsOpen(false);
        setActiveIndex(-1);
        break;
    }
  };

  /* ---- Click outside to close ---- */
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () =>
      document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  /* ---- Cleanup debounce on unmount ---- */
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative mx-auto w-full max-w-2xl">
      {/* Search input */}
      <div className="relative">
        {/* Magnifying glass icon */}
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
          <svg
            className="h-5 w-5 text-abn-grey"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
            />
          </svg>
        </div>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (results.length > 0) setIsOpen(true);
          }}
          placeholder="Search by Business Contact Number..."
          className="w-full rounded-full border border-gray-300 bg-white py-3.5 pl-12 pr-12 text-base shadow-sm transition-all placeholder:text-abn-grey-light focus:border-abn-teal focus:shadow-md focus:ring-2 focus:ring-abn-teal/30 focus:outline-none"
        />

        {/* Loading spinner */}
        {loading && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-4">
            <Spinner size="sm" />
          </div>
        )}
      </div>

      {/* Dropdown results */}
      {isOpen && (
        <div className="absolute z-50 mt-2 w-full overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg">
          {results.length > 0 ? (
            <ul className="max-h-80 overflow-y-auto py-1">
              {results.map((result, idx) => (
                <li key={result.bcn}>
                  <button
                    type="button"
                    className={`flex w-full items-center gap-4 px-4 py-3 text-left transition-colors hover:bg-abn-teal-light ${
                      idx === activeIndex ? "bg-abn-teal-light" : ""
                    }`}
                    onClick={() => selectResult(result)}
                    onMouseEnter={() => setActiveIndex(idx)}
                  >
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-abn-teal/10">
                      <svg
                        className="h-5 w-5 text-abn-teal"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
                        />
                      </svg>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-gray-900">
                        {result.bcn}
                      </p>
                      <p className="truncate text-xs text-abn-grey">
                        {result.name}
                      </p>
                    </div>
                    <span className="shrink-0 rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-abn-grey-dark">
                      {result.transaction_count} txn{result.transaction_count !== 1 ? "s" : ""}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : hasSearched && !loading ? (
            <div className="px-4 py-6 text-center text-sm text-abn-grey">
              No results found for &ldquo;{query}&rdquo;
            </div>
          ) : null}

          {!hasSearched && !loading && (
            <div className="px-4 py-6 text-center text-sm text-abn-grey-light">
              Start typing to search...
            </div>
          )}
        </div>
      )}
    </div>
  );
}
