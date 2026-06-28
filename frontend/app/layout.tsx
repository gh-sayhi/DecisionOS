import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DecisionOS",
  description: "AI Decision Operating System for executive decisions, risk reasoning, budget planning and next actions"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
