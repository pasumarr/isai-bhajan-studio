"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePlayer } from "../context/PlayerContext";
import API_BASE from "../utils/api";

const formatTime = (secs) => {
  if (isNaN(secs)) return "0:00";
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s < 10 ? "0" : ""}${s}`;
};

export default function NowPlaying() {
  const { currentBhajan, isPlaying, togglePlay, playBhajan, currentTime, duration, seek } = usePlayer();
  const [related, setRelated] = useState([]);

  useEffect(() => {
    if (currentBhajan?.id) {
      fetch(`${API_BASE}/api/bhajans/${currentBhajan.id}/related?limit=8`)
        .then((r) => r.json())
        .then(setRelated)
        .catch(console.error);
    }
  }, [currentBhajan?.id]);

  if (!currentBhajan) {
    return (
      <div className="now-playing-empty">
        <div className="np-empty-icon">🎵</div>
        <h2>Nothing Playing</h2>
        <p>Select a bhajan from Search to start listening</p>
        <Link href="/search" className="hero-cta">Go to Search</Link>
      </div>
    );
  }

  // YouTube embed
  let embedUrl = "";
  if (currentBhajan.video_url) {
    try {
      let vid = "";
      if (currentBhajan.video_url.includes("youtu.be/")) vid = currentBhajan.video_url.split("youtu.be/")[1]?.split("?")[0];
      else if (currentBhajan.video_url.includes("youtube.com/watch")) vid = new URL(currentBhajan.video_url).searchParams.get("v");
      if (vid) embedUrl = `https://www.youtube.com/embed/${vid}`;
    } catch (e) {}
  }

  return (
    <div className="now-playing-page">
      {/* Header gradient */}
      <div className="np-hero">
        <div className="np-hero-bg" />
        <div className="np-hero-content">
          <div className="np-play-btn" onClick={togglePlay}>
            {isPlaying ? "⏸" : "▶"}
          </div>
          <h1 className="np-title">{currentBhajan.title}</h1>
          <div className="np-badges">
            {currentBhajan.deity && <span className="badge b-deity">{currentBhajan.deity}</span>}
            {currentBhajan.raga && <span className="badge b-raga">Raga: {currentBhajan.raga}</span>}
            {currentBhajan.beat && <span className="badge b-beat">Beat: {currentBhajan.beat}</span>}
            {currentBhajan.tempo && <span className="badge b-tempo">Tempo: {currentBhajan.tempo}</span>}
            {currentBhajan.level && <span className="badge b-level">{currentBhajan.level}</span>}
            {currentBhajan.language && <span className="badge b-lang">{currentBhajan.language}</span>}
          </div>
        </div>
      </div>

      {/* Media */}
      <div className="np-media-section">
        {embedUrl && (
          <div className="np-video">
            <iframe width="100%" height="300" src={embedUrl} title="Video" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
          </div>
        )}
        {currentBhajan.audio_url && (
          <div className="custom-player-controls" style={{
            background: "rgba(255, 255, 255, 0.05)",
            backdropFilter: "blur(10px)",
            borderRadius: "16px",
            padding: "1.5rem",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
            width: "100%",
            maxWidth: "500px",
            margin: "1.5rem auto"
          }}>
            {/* Progress Bar */}
            <div className="progress-container" style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <input
                type="range"
                min="0"
                max={duration || 100}
                value={currentTime}
                onChange={(e) => seek(parseFloat(e.target.value))}
                style={{
                  width: "100%",
                  accentColor: "var(--accent, #ff5722)",
                  cursor: "pointer",
                  height: "6px",
                  borderRadius: "3px"
                }}
              />
              <div className="time-display" style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "rgba(255, 255, 255, 0.6)" }}>
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
            
            {/* Control buttons */}
            <div className="control-buttons" style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "2rem" }}>
              <button 
                onClick={togglePlay} 
                style={{
                  background: "var(--accent, #ff5722)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "50%",
                  width: "56px",
                  height: "56px",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 4px 15px rgba(255, 87, 34, 0.4)",
                  transition: "transform 0.2s"
                }}
                className="play-pause-btn"
              >
                {isPlaying ? "⏸" : "▶"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Lyrics */}
      <div className="np-lyrics-section">
        <h2>Lyrics</h2>
        <pre className="np-lyrics">{currentBhajan.lyrics}</pre>
      </div>

      {/* Related */}
      {related.length > 0 && (
        <div className="np-related">
          <h2>Related Bhajans</h2>
          <div className="related-grid">
            {related.map((b) => (
              <div key={b.id} className="related-card" onClick={() => playBhajan(b)}>
                <span className="related-icon">{b.audio_url ? "♫" : "🎵"}</span>
                <div className="related-info">
                  <span className="related-title">{b.title}</span>
                  <span className="related-deity">{b.deity}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
