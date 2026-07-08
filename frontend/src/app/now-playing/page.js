"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePlayer } from "../context/PlayerContext";
import API_BASE from "../utils/api";

export default function NowPlaying() {
  const { currentBhajan, isPlaying, togglePlay } = usePlayer();
  const [related, setRelated] = useState([]);
  const { playBhajan } = usePlayer();

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
          <div className="np-audio">
            <audio controls src={currentBhajan.audio_url} autoPlay={isPlaying} style={{ width: "100%" }} />
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
