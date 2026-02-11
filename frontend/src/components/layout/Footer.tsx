import { BRAND } from "@/lib/branding";

export default function Footer() {
  return (
    <footer className="w-full border-t border-gray-200 bg-gray-50">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <p className="text-xs text-abn-grey">
          {BRAND.copyrightTemplate(new Date().getFullYear())}
        </p>
        <p className="text-xs text-abn-grey-light">
          {BRAND.footerTagline}
        </p>
      </div>
    </footer>
  );
}
