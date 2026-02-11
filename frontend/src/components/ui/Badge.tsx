import React from "react";

type BadgeVariant = "success" | "warning" | "danger" | "info" | "default";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  success:
    "bg-risk-low/15 text-risk-low border border-risk-low/30",
  warning:
    "bg-risk-medium/15 text-yellow-800 border border-risk-medium/30",
  danger:
    "bg-risk-critical/15 text-risk-critical border border-risk-critical/30",
  info: "bg-abn-teal/10 text-abn-teal-dark border border-abn-teal/30",
  default: "bg-gray-100 text-gray-700 border border-gray-200",
};

export default function Badge({
  children,
  variant = "default",
  className = "",
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
