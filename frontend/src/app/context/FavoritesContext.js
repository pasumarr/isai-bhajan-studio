"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import { db } from "../utils/firebase";
import { useAuth } from "./AuthContext";
import {
  doc,
  collection,
  onSnapshot,
  setDoc,
  deleteDoc,
  serverTimestamp,
} from "firebase/firestore";

const FavoritesContext = createContext();

export function FavoritesProvider({ children }) {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState({}); // { [bhajanId]: bhajanData }
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      setFavorites({});
      return;
    }

    setLoading(true);

    // Real-time listener on the user's favorites subcollection
    // Path: users/{uid}/favorites/{bhajanId}
    const favRef = collection(db, "users", user.uid, "favorites");
    const unsubscribe = onSnapshot(
      favRef,
      (snapshot) => {
        const favMap = {};
        snapshot.forEach((docSnap) => {
          favMap[docSnap.id] = docSnap.data();
        });
        setFavorites(favMap);
        setLoading(false);
      },
      (error) => {
        console.error("Favorites listener error:", error);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [user]);

  const toggleFavorite = async (bhajan) => {
    if (!user) return;

    const bhajanId = String(bhajan.id);
    const favDocRef = doc(db, "users", user.uid, "favorites", bhajanId);

    if (favorites[bhajanId]) {
      // Remove from favorites
      await deleteDoc(favDocRef);
    } else {
      // Add to favorites — store key metadata for display without extra fetches
      await setDoc(favDocRef, {
        id: bhajan.id,
        title: bhajan.title,
        deity: bhajan.deity || "",
        raga: bhajan.raga || "",
        tempo: bhajan.tempo || "",
        audio_url: bhajan.audio_url || "",
        video_url: bhajan.video_url || "",
        addedAt: serverTimestamp(),
      });
    }
  };

  const isFavorite = (bhajanId) => Boolean(favorites[String(bhajanId)]);

  const favoritesArray = Object.values(favorites).sort((a, b) =>
    (a.addedAt?.seconds || 0) > (b.addedAt?.seconds || 0) ? -1 : 1
  );

  return (
    <FavoritesContext.Provider value={{ favorites, favoritesArray, loading, toggleFavorite, isFavorite }}>
      {children}
    </FavoritesContext.Provider>
  );
}

export const useFavorites = () => useContext(FavoritesContext);
