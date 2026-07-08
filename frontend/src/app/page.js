"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePlayer } from "./context/PlayerContext";
import API_BASE from "./utils/api";

export default function Home() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { playBhajan } = usePlayer();

  useEffect(() => {
    fetch(`${API_BASE}/api/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner" />
        <p>Loading ISai Bhajan Studio...</p>
      </div>
    );
  }

  return (
    <div className="home-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-glow" />
        <h1 className="hero-title">ISai Bhajan Studio</h1>
        <p className="hero-subtitle">Discover the divine rhythms — 3,600+ devotional songs at your fingertips</p>
        <Link href="/search" className="hero-cta">
          🔍 Explore All Bhajans
        </Link>
      </section>

      {/* Stats */}
      {stats && (
        <section className="stats-section">
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-number">{stats.total_bhajans.toLocaleString()}</span>
              <span className="stat-label">Total Bhajans</span>
            </div>
            <div className="stat-card accent-blue">
              <span className="stat-number">{stats.with_audio.toLocaleString()}</span>
              <span className="stat-label">With Audio</span>
            </div>
            <div className="stat-card accent-red">
              <span className="stat-number">{stats.with_video.toLocaleString()}</span>
              <span className="stat-label">With Video</span>
            </div>
          </div>
        </section>
      )}

      {/* Browse by Deity */}
      {stats && stats.deities && (
        <section className="deity-section">
          <h2 className="section-title">Browse by Deity</h2>
          <div className="deity-grid">
            {stats.deities.map((d) => (
              <Link
                key={d.name}
                href={`/search?deity=${encodeURIComponent(d.name)}`}
                className="deity-card"
              >
                <span className="deity-icon">{getDeityEmoji(d.name)}</span>
                <span className="deity-name">{d.name}</span>
                <span className="deity-count">{d.count} songs</span>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function getDeityEmoji(name) {
  const map = {
    krishna: "🪈", rama: "🏹", shiva: "🔱", devi: "🌺", ganesha: "🐘",
    sai: "🙏", guru: "🙏", sarva_dharma: "☮️", jesus: "✝️", allah: "☪️",
    buddha: "☸️", narayana: "🌊", gayathri: "☀️", vittala: "🎶",
    subrahmanya: "🦚", narasimha: "🦁", anjaneya: "🐒", surya: "☀️",
    ayyappa: "🪔", jehovah: "✡️",
  };
  return map[name.toLowerCase().replace(/\s/g, "_")] || "🎵";
}
