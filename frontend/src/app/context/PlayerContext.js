"use client";
import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from "react";

const PlayerContext = createContext(null);

export function PlayerProvider({ children }) {
  const [currentBhajan, setCurrentBhajan] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef(null);

  // Sync isPlaying state with audio element playback
  useEffect(() => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.play().catch(console.error);
    } else {
      audioRef.current.pause();
    }
  }, [isPlaying]);

  // Sync source URL with current bhajan
  useEffect(() => {
    if (!audioRef.current) return;
    if (currentBhajan?.audio_url) {
      audioRef.current.src = currentBhajan.audio_url;
      if (isPlaying) {
        audioRef.current.play().catch(console.error);
      }
    } else {
      audioRef.current.src = "";
      setCurrentTime(0);
      setDuration(0);
    }
  }, [currentBhajan?.audio_url]);

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

  const seek = useCallback((time) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  }, []);

  return (
    <PlayerContext.Provider value={{ currentBhajan, isPlaying, playBhajan, togglePlay, stop, currentTime, duration, seek }}>
      {children}
      <audio
        ref={audioRef}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => {
          setIsPlaying(false);
          setCurrentTime(0);
        }}
        onTimeUpdate={(e) => setCurrentTime(e.target.currentTime)}
        onDurationChange={(e) => setDuration(e.target.duration)}
      />
    </PlayerContext.Provider>
  );
}

export function usePlayer() {
  const ctx = useContext(PlayerContext);
  if (!ctx) throw new Error("usePlayer must be used inside PlayerProvider");
  return ctx;
}
