/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║  BRANDING CONFIGURATION                                        ║
 * ║  Change bank name, colors, and text here.                      ║
 * ║  All values propagate across the entire application.            ║
 * ╚══════════════════════════════════════════════════════════════════╝
 *
 * CSS color tokens are defined in: src/app/globals.css
 * (search for ":root" and "@theme inline" blocks)
 */

export const BRAND = {
  /** Bank / organization name shown in header, footer, metadata */
  name: "ABC Bank",

  /** Full legal name for footer copyright */
  legalName: "ABC Bank N.V.",

  /** Application title shown in browser tab */
  appTitle: "AML Transaction Monitor",

  /** Subtitle below the app title */
  appSubtitle: "AML Transaction Overview Tool",

  /** Meta description for SEO / browser */
  metaDescription:
    "ABC Bank AML Transaction Overview Tool for compliance investigations",

  /** Landing page heading */
  landingHeading: "Transaction Monitor",

  /** Landing page subheading */
  landingSubheading:
    "Search a customer by Business Contact Number to begin investigation",

  /** Footer tagline */
  footerTagline: "AML Compliance Tool — MVP1",

  /** Copyright template (year is injected at runtime) */
  copyrightTemplate: (year: number) =>
    `\u00A9 ${year} ${BRAND.legalName}. All rights reserved.`,
} as const;
