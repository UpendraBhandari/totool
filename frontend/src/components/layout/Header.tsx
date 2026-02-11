import Link from "next/link";
import { BRAND } from "@/lib/branding";

export default function Header() {
  return (
    <header className="h-16 w-full bg-abn-teal">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <span className="text-xl font-bold tracking-wide text-white">
            {BRAND.name}
          </span>
          <span className="hidden text-sm font-medium text-white/80 sm:inline">
            |
          </span>
          <span className="hidden text-sm font-medium text-white/80 sm:inline">
            {BRAND.appSubtitle}
          </span>
        </Link>

        <nav className="flex items-center gap-4">
          <Link
            href="/"
            className="text-sm font-medium text-white/90 transition-colors hover:text-white"
          >
            Home
          </Link>
          <Link
            href="/upload"
            className="text-sm font-medium text-white/90 transition-colors hover:text-white"
          >
            Upload
          </Link>
        </nav>
      </div>
    </header>
  );
}
