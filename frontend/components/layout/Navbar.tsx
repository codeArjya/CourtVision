"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Games" },
  { href: "/predictions", label: "Predictions" },
  { href: "/takes", label: "Takes" },
  { href: "/news", label: "News" },
];

export default function Navbar() {
  const pathname = usePathname();
  return (
    <nav className="fixed top-7 left-0 right-0 z-40 h-14 flex items-center px-6 bg-surface/90 backdrop-blur-md border-b border-border">
      {/* Brand */}
      <span className="font-black text-xl mr-auto flex items-center gap-2">
        <span className="text-orange">🏀</span>
        <span className="text-primary">Court</span>
        <span className="text-orange">IQ</span>
      </span>

      {/* Nav links */}
      <div className="flex gap-6">
        {links.map(({ href, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={
                active
                  ? "text-orange text-sm font-semibold border-b-2 border-orange pb-0.5 transition-colors"
                  : "text-secondary hover:text-primary text-sm font-medium transition-colors"
              }
            >
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
