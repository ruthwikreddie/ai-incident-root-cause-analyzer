import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Incident Intelligence | AI Root Cause Analyzer",
  description:
    "AI-assisted incident analysis and root cause intelligence platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
