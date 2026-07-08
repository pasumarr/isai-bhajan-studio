"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { usePlayer } from "../context/PlayerContext";

const NAV_ITEMS = [
  { href: "/", icon: "🏠", label: "Home" },
  { href: "/search", icon: "🔍", label: "Search" },
  { href: "/coordinate", icon: "💬", label: "Coordinate" },
  { href: "/contribute", icon: "➕", label: "Contribute" },
  { href: "/profile", icon: "👤", label: "Profile" },
];

export default function AppShell({ children }) {
  const pathname = usePathname();
  const { currentBhajan, isPlaying, togglePlay } = usePlayer();

  return (
    <>
      <main className="app-main">{children}</main>

      {/* Mini-Player */}
      {currentBhajan && (
        <div className="mini-player">
          <Link href="/now-playing" className="mini-player-info">
            <div className="mini-player-pulse" />
            <div className="mini-player-details">
              <span className="mini-player-title">{currentBhajan.title}</span>
              <span className="mini-player-sub">{currentBhajan.deity}</span>
            </div>
          </Link>
          <button className="mini-player-btn" onClick={togglePlay}>
            {isPlaying ? "⏸" : "▶"}
          </button>
        </div>
      )}

      {/* Bottom Navigation */}
      <nav className="bottom-nav">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item ${pathname === item.href ? "active" : ""}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>
    </>
  );
}
