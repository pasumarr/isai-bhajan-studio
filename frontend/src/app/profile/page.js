"use client";
import React from "react";
import { useAuth } from "../context/AuthContext";
import { useFavorites } from "../context/FavoritesContext";
import { usePlayer } from "../context/PlayerContext";

export default function Profile() {
  const { user, loading, authError, setAuthError, loginWithGoogle, logout } = useAuth();
  const { favoritesArray, loading: favLoading, toggleFavorite } = useFavorites();
  const { playBhajan, currentBhajan, isPlaying, togglePlay } = usePlayer();

  if (loading) {
    return (
      <div className="coming-soon-page">
        <div className="spinner" style={{ width: "48px", height: "48px", border: "4px solid rgba(255,255,255,0.1)", borderTop: "4px solid var(--accent, #ff5722)", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
        <p style={{ marginTop: "1rem", color: "rgba(255,255,255,0.6)" }}>Loading your profile...</p>
      </div>
    );
  }

  /* ── Not signed in ────────────────────── */
  if (!user) {
    return (
      <div className="coming-soon-page" style={{ gap: "1.5rem" }}>
        <div className="cs-icon">👤</div>
        <h1>Your Profile</h1>
        <p style={{ color: "rgba(255,255,255,0.65)", maxWidth: "360px", textAlign: "center", lineHeight: "1.6" }}>
          Sign in with Google to save your favourite bhajans, build custom setlists, and join the Bhajan community.
        </p>

        {authError && (
          <div style={{ background: "rgba(255,80,80,0.12)", border: "1px solid rgba(255,80,80,0.35)", borderRadius: "10px", padding: "1rem 1.25rem", maxWidth: "420px", whiteSpace: "pre-line", fontSize: "0.85rem", color: "#ff8080", lineHeight: "1.6", textAlign: "left" }}>
            {authError}
            <button onClick={() => setAuthError(null)} style={{ display: "block", marginTop: "0.75rem", background: "none", border: "none", color: "#ff8080", textDecoration: "underline", cursor: "pointer", fontSize: "0.8rem" }}>Dismiss</button>
          </div>
        )}

        <button
          onClick={loginWithGoogle}
          style={{ display: "flex", alignItems: "center", gap: "12px", background: "#fff", color: "#333", border: "none", borderRadius: "10px", padding: "13px 28px", fontSize: "1rem", fontWeight: "600", cursor: "pointer", boxShadow: "0 4px 20px rgba(0,0,0,0.3)", transition: "transform 0.15s, box-shadow 0.15s" }}
          onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 8px 28px rgba(0,0,0,0.4)"; }}
          onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 20px rgba(0,0,0,0.3)"; }}
        >
          <svg width="20" height="20" viewBox="0 0 48 48">
            <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
            <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,19.026,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
            <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
            <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
          </svg>
          Sign in with Google
        </button>

        <div className="cs-features" style={{ marginTop: "1rem" }}>
          <div className="cs-feature"><span>❤️</span><span>Favourite bhajans</span></div>
          <div className="cs-feature"><span>📚</span><span>Custom setlists</span></div>
          <div className="cs-feature"><span>🏅</span><span>Contribution badges</span></div>
        </div>
      </div>
    );
  }

  /* ── Signed in ──────────────────────── */
  return (
    <div style={{ padding: "1.5rem 1rem 6rem", maxWidth: "680px", margin: "0 auto", color: "#fff" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ position: "relative", flexShrink: 0 }}>
          {user.photoURL ? (
            <img src={user.photoURL} alt="Profile" style={{ width: "64px", height: "64px", borderRadius: "50%", border: "2px solid var(--accent, #ff5722)" }} />
          ) : (
            <div style={{ width: "64px", height: "64px", borderRadius: "50%", background: "var(--accent, #ff5722)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.75rem", fontWeight: "bold" }}>
              {(user.displayName || user.email || "?").charAt(0).toUpperCase()}
            </div>
          )}
          <div style={{ position: "absolute", bottom: "2px", right: "2px", width: "14px", height: "14px", background: "#4CAF50", borderRadius: "50%", border: "2px solid #1a1a2e" }} />
        </div>
        <div>
          <h1 style={{ margin: "0 0 0.2rem", fontSize: "1.4rem" }}>{user.displayName || "User"}</h1>
          <p style={{ margin: 0, color: "rgba(255,255,255,0.5)", fontSize: "0.85rem" }}>{user.email}</p>
        </div>
        <button onClick={logout} style={{ marginLeft: "auto", background: "rgba(255,255,255,0.07)", color: "rgba(255,255,255,0.65)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: "8px", padding: "8px 16px", fontSize: "0.85rem", fontWeight: "600", cursor: "pointer", transition: "background 0.2s", flexShrink: 0 }}
          onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.12)"}
          onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.07)"}
        >Sign Out</button>
      </div>

      {/* Favourites Section */}
      <div>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "8px" }}>
          ❤️ Favourite Bhajans
          <span style={{ background: "var(--accent, #ff5722)", borderRadius: "20px", padding: "2px 10px", fontSize: "0.75rem", fontWeight: "700" }}>
            {favoritesArray.length}
          </span>
        </h2>

        {favLoading ? (
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.9rem" }}>Loading favourites...</p>
        ) : favoritesArray.length === 0 ? (
          <div style={{ background: "rgba(255,255,255,0.04)", borderRadius: "12px", padding: "2rem", textAlign: "center", color: "rgba(255,255,255,0.4)" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🤍</div>
            <p style={{ margin: 0 }}>No favourites yet — tap 🤍 on any bhajan to save it here.</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {favoritesArray.map((b) => {
              const isCurrent = currentBhajan?.id === b.id;
              return (
                <div key={b.id} style={{ display: "flex", alignItems: "center", gap: "0.75rem", background: "rgba(255,255,255,0.05)", borderRadius: "10px", padding: "0.75rem 1rem", transition: "background 0.2s" }}
                  onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.09)"}
                  onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.05)"}
                >
                  {/* Play button */}
                  <button
                    onClick={() => isCurrent ? togglePlay() : playBhajan(b)}
                    style={{ background: isCurrent && isPlaying ? "rgba(255,87,34,0.2)" : "var(--accent, #ff5722)", border: "none", borderRadius: "50%", width: "36px", height: "36px", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "0.9rem", flexShrink: 0, color: "#fff", transition: "opacity 0.2s" }}
                  >
                    {isCurrent && isPlaying ? "⏸" : "▶"}
                  </button>

                  {/* Info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ margin: "0 0 0.1rem", fontWeight: "600", fontSize: "0.95rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{b.title}</p>
                    <p style={{ margin: 0, color: "rgba(255,255,255,0.45)", fontSize: "0.78rem" }}>
                      {[b.deity, b.raga, b.tempo].filter(Boolean).join(" · ")}
                    </p>
                  </div>

                  {/* Remove */}
                  <button
                    onClick={() => toggleFavorite(b)}
                    title="Remove from favourites"
                    style={{ background: "none", border: "none", fontSize: "1.1rem", cursor: "pointer", padding: "4px", opacity: 0.7, transition: "opacity 0.2s", flexShrink: 0 }}
                    onMouseEnter={e => e.currentTarget.style.opacity = "1"}
                    onMouseLeave={e => e.currentTarget.style.opacity = "0.7"}
                  >
                    ❤️
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
