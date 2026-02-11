import type { CustomerOverview } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";

interface CustomerHeaderProps {
  customer: CustomerOverview;
}

export default function CustomerHeader({ customer }: CustomerHeaderProps) {
  const totalVolume = customer.transactions.reduce(
    (sum, t) => sum + t.amount,
    0
  );

  const dates = customer.transactions
    .map((t) => new Date(t.date).getTime())
    .filter((d) => !isNaN(d));
  const firstDate = dates.length > 0 ? new Date(Math.min(...dates)) : null;
  const lastDate = dates.length > 0 ? new Date(Math.max(...dates)) : null;

  const uniqueCounterparties = new Set(
    customer.transactions.flatMap((t) => [t.sender, t.receiver])
  ).size;

  return (
    <div className="rounded-lg border border-gray-200 border-l-abn-teal border-l-4 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        {/* Left: identification */}
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-abn-grey">
            Business Contact Number
          </p>
          <h2 className="mt-1 text-2xl font-bold text-gray-900">
            {customer.business_contact_number}
          </h2>
          {customer.customer_name && (
            <p className="mt-0.5 text-sm text-abn-grey-dark">
              {customer.customer_name}
            </p>
          )}
        </div>

        {/* Right: key metrics */}
        <div className="grid grid-cols-2 gap-x-8 gap-y-2 sm:grid-cols-4">
          <Metric
            label="Total Volume"
            value={formatCurrency(totalVolume)}
          />
          <Metric
            label="Transactions"
            value={customer.transactions.length.toLocaleString()}
          />
          <Metric
            label="Date Range"
            value={
              firstDate && lastDate
                ? `${formatDate(firstDate.toISOString())} - ${formatDate(lastDate.toISOString())}`
                : "-"
            }
          />
          <Metric
            label="Counterparties"
            value={uniqueCounterparties.toLocaleString()}
          />
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] font-medium uppercase tracking-wider text-abn-grey-light">
        {label}
      </p>
      <p className="text-sm font-semibold text-gray-900">{value}</p>
    </div>
  );
}
