"use client";

import { useState, useMemo } from "react";
import type { Transaction } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import Badge from "@/components/ui/Badge";

interface TransactionTableProps {
  transactions: Transaction[];
}

type SortKey =
  | "date"
  | "amount"
  | "sender"
  | "receiver"
  | "iban"
  | "currency"
  | "transaction_type"
  | "flags";

type SortDir = "asc" | "desc";

const PAGE_SIZE = 20;

export default function TransactionTable({
  transactions,
}: TransactionTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [filter, setFilter] = useState("");
  const [page, setPage] = useState(0);

  /* ---- Filter ---- */
  const filtered = useMemo(() => {
    if (!filter.trim()) return transactions;
    const q = filter.toLowerCase();
    return transactions.filter(
      (t) =>
        t.sender.toLowerCase().includes(q) ||
        t.receiver.toLowerCase().includes(q) ||
        (t.iban ?? "").toLowerCase().includes(q) ||
        (t.description ?? "").toLowerCase().includes(q) ||
        (t.transaction_type ?? "").toLowerCase().includes(q) ||
        t.flags.some((f) => f.toLowerCase().includes(q)) ||
        String(t.amount).includes(q) ||
        t.date.includes(q)
    );
  }, [transactions, filter]);

  /* ---- Sort ---- */
  const sorted = useMemo(() => {
    const arr = [...filtered];
    arr.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "date":
          cmp =
            new Date(a.date).getTime() - new Date(b.date).getTime();
          break;
        case "amount":
          cmp = a.amount - b.amount;
          break;
        case "sender":
          cmp = a.sender.localeCompare(b.sender);
          break;
        case "receiver":
          cmp = a.receiver.localeCompare(b.receiver);
          break;
        case "iban":
          cmp = (a.iban ?? "").localeCompare(b.iban ?? "");
          break;
        case "currency":
          cmp = a.currency.localeCompare(b.currency);
          break;
        case "transaction_type":
          cmp = (a.transaction_type ?? "").localeCompare(
            b.transaction_type ?? ""
          );
          break;
        case "flags":
          cmp = a.flags.length - b.flags.length;
          break;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });
    return arr;
  }, [filtered, sortKey, sortDir]);

  /* ---- Pagination ---- */
  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages - 1);
  const pageData = sorted.slice(
    safePage * PAGE_SIZE,
    (safePage + 1) * PAGE_SIZE
  );

  /* ---- Toggle sort ---- */
  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(0);
  };

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortKey !== column)
      return (
        <svg className="ml-1 inline h-3 w-3 text-gray-300" viewBox="0 0 10 14" fill="currentColor">
          <path d="M5 0L10 5H0L5 0ZM5 14L0 9H10L5 14Z" />
        </svg>
      );
    return sortDir === "asc" ? (
      <svg className="ml-1 inline h-3 w-3 text-abn-teal" viewBox="0 0 10 7" fill="currentColor">
        <path d="M5 0L10 7H0L5 0Z" />
      </svg>
    ) : (
      <svg className="ml-1 inline h-3 w-3 text-abn-teal" viewBox="0 0 10 7" fill="currentColor">
        <path d="M5 7L0 0H10L5 7Z" />
      </svg>
    );
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
        <h3 className="text-sm font-semibold text-gray-900">
          Transactions ({filtered.length})
        </h3>
        <input
          type="text"
          value={filter}
          onChange={(e) => {
            setFilter(e.target.value);
            setPage(0);
          }}
          placeholder="Filter transactions..."
          className="w-64 rounded-md border border-gray-300 px-3 py-1.5 text-sm placeholder:text-abn-grey-light focus:border-abn-teal focus:ring-1 focus:ring-abn-teal/30 focus:outline-none"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/50">
              {(
                [
                  ["date", "Date"],
                  ["amount", "Amount"],
                  ["sender", "Sender"],
                  ["receiver", "Receiver"],
                  ["iban", "IBAN"],
                  ["currency", "Currency"],
                  ["transaction_type", "Type"],
                  ["flags", "Flags"],
                ] as [SortKey, string][]
              ).map(([key, label]) => (
                <th
                  key={key}
                  className="cursor-pointer px-4 py-3 text-xs font-semibold uppercase tracking-wider text-abn-grey select-none hover:text-abn-teal-dark"
                  onClick={() => toggleSort(key)}
                >
                  {label}
                  <SortIcon column={key} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageData.length === 0 ? (
              <tr>
                <td
                  colSpan={8}
                  className="px-4 py-8 text-center text-sm text-abn-grey"
                >
                  No transactions match your filter.
                </td>
              </tr>
            ) : (
              pageData.map((t) => (
                <tr
                  key={t.index}
                  className={`border-b border-gray-50 transition-colors hover:bg-gray-50 ${
                    t.flags.length > 0 ? "bg-flag-bg" : ""
                  }`}
                >
                  <td className="whitespace-nowrap px-4 py-2.5 text-xs text-gray-700">
                    {formatDate(t.date)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5 text-xs font-medium text-gray-900">
                    {formatCurrency(t.amount, t.currency)}
                  </td>
                  <td className="max-w-[140px] truncate px-4 py-2.5 text-xs text-gray-700">
                    {t.sender}
                  </td>
                  <td className="max-w-[140px] truncate px-4 py-2.5 text-xs text-gray-700">
                    {t.receiver}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5 text-xs font-mono text-gray-500">
                    {t.iban ?? "-"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5 text-xs text-gray-500">
                    {t.currency}
                  </td>
                  <td className="whitespace-nowrap px-4 py-2.5 text-xs text-gray-500">
                    {t.transaction_type ?? "-"}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex flex-wrap gap-1">
                      {t.flags.map((flag, i) => (
                        <Badge key={i} variant="danger">
                          {flag}
                        </Badge>
                      ))}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between border-t border-gray-100 px-6 py-3">
        <p className="text-xs text-abn-grey">
          Showing {safePage * PAGE_SIZE + 1}&ndash;
          {Math.min((safePage + 1) * PAGE_SIZE, sorted.length)} of{" "}
          {sorted.length}
        </p>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={safePage === 0}
            className="rounded-md border border-gray-200 px-3 py-1 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Prev
          </button>
          <span className="text-xs text-abn-grey">
            Page {safePage + 1} of {totalPages}
          </span>
          <button
            type="button"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={safePage >= totalPages - 1}
            className="rounded-md border border-gray-200 px-3 py-1 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
