import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import ScoreTicker from "@/components/layout/ScoreTicker";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "CourtVision — Ball Knowledge AI",
  description:
    "NBA live stats dashboard, AI predictions, and media takes feed powered by Gemini.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-bg text-primary font-sans">
        <Providers>
          {/* Score ticker: fixed top-0 h-7 (28px) */}
          <ScoreTicker />
          {/* Navbar: fixed top-7 h-14 (56px) → total header = 84px */}
          <Navbar />
          {/* Main: pt-[84px] to clear both fixed bars */}
          <main className="pt-[84px] min-h-screen">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
