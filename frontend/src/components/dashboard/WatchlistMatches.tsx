import type { WatchlistMatch } from "@/lib/types";

interface WatchlistMatchesProps {
  matches: WatchlistMatch[];
}

export default function WatchlistMatches({ matches }: WatchlistMatchesProps) {
  if (matches.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-gray-900">
          Watchlist Matches
        </h3>
        <div className="flex items-center gap-2 text-sm text-abn-grey">
          <svg
            className="h-5 w-5 text-risk-low"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          No watchlist matches found
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">
        Watchlist Matches ({matches.length})
      </h3>
      <div className="space-y-3">
        {matches.map((match, idx) => {
          const pct = Math.round(match.match_score);
          const barColor =
            pct >= 85
              ? "bg-risk-critical"
              : pct >= 70
                ? "bg-risk-high"
                : "bg-risk-medium";

          return (
            <div
              key={idx}
              className="rounded-lg border border-gray-100 bg-gray-50 p-4"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-gray-900">
                    {match.matched_entity}
                  </p>
                  <p className="text-xs text-abn-grey">
                    Matched against:{" "}
                    <span className="font-medium text-gray-700">
                      {match.watchlist_entry}
                    </span>
                  </p>
                  <p className="mt-0.5 text-xs text-abn-grey-light">
                    Field: {match.match_field}
                  </p>
                </div>
                <span className="shrink-0 text-lg font-bold text-gray-900">
                  {pct}%
                </span>
              </div>

              {/* Confidence progress bar */}
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
                <div
                  className={`h-full rounded-full ${barColor} transition-all`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              {match.transaction_indices.length > 0 && (
                <p className="mt-2 text-xs text-abn-grey">
                  Found in {match.transaction_indices.length} transaction
                  {match.transaction_indices.length !== 1 ? "s" : ""}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
