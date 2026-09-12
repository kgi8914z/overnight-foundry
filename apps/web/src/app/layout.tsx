import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Overnight Foundry — 길드 홀",
  description: "아침 8분 선택/도태 공장",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
