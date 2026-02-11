"use client";

interface TabItem {
  id: string;
  label: string;
  badge?: { count: number; variant?: "neutral" | "alert" };
}

interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export default function Tabs({ tabs, activeTab, onTabChange }: TabsProps) {
  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex gap-6" aria-label="Tabs">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`relative whitespace-nowrap border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
                isActive
                  ? "border-abn-teal text-abn-teal"
                  : "border-transparent text-abn-grey hover:border-gray-300 hover:text-gray-700"
              }`}
            >
              {tab.label}
              {tab.badge !== undefined && tab.badge.count > 0 && (
                <span
                  className={`ml-2 inline-flex min-w-[20px] items-center justify-center rounded-full px-1.5 py-0.5 text-[10px] font-semibold leading-none ${
                    tab.badge.variant === "alert"
                      ? "bg-risk-critical/10 text-risk-critical"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {tab.badge.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
