"use client";
import React, { createContext, useContext, useState, useCallback } from "react";

const PlayerContext = createContext(null);

export function PlayerProvider({ children }) {
  const [currentBhajan, setCurrentBhajan] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const playBhajan = useCallback((bhajan) => {
    setCurrentBhajan(bhajan);
    setIsPlaying(true);
  }, []);

  const togglePlay = useCallback(() => {
    setIsPlaying((p) => !p);
  }, []);

  const stop = useCallback(() => {
    setIsPlaying(false);
    setCurrentBhajan(null);
  }, []);

  return (
    <PlayerContext.Provider value={{ currentBhajan, isPlaying, playBhajan, togglePlay, stop }}>
      {children}
    </PlayerContext.Provider>
  );
}

export function usePlayer() {
  const ctx = useContext(PlayerContext);
  if (!ctx) throw new Error("usePlayer must be used inside PlayerProvider");
  return ctx;
}
