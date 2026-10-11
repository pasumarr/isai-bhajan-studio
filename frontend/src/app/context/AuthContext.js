"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import { auth } from "../utils/firebase";
import {
  onAuthStateChanged,
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
  GoogleAuthProvider,
  signOut,
} from "firebase/auth";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    // Handle redirect result when page loads back after Google sign-in
    getRedirectResult(auth)
      .then((result) => {
        if (result?.user) {
          setUser(result.user);
          setAuthError(null);
        }
      })
      .catch((error) => {
        console.error("Redirect result error:", error.code, error.message);
        if (error.code === "auth/unauthorized-domain") {
          setAuthError(
            "Sign-in blocked: localhost is not yet authorized in the Firebase Console. " +
            "Go to Firebase Console → Authentication → Settings → Authorized Domains → Add 'localhost'."
          );
        } else {
          setAuthError(error.message);
        }
      });

    // Listen for auth state changes (persists across page refreshes)
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    setAuthError(null);
    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: "select_account" });

    try {
      // Try popup first (better UX) — falls back to redirect if blocked
      const result = await signInWithPopup(auth, provider);
      setUser(result.user);
    } catch (popupError) {
      if (
        popupError.code === "auth/popup-blocked" ||
        popupError.code === "auth/cancelled-popup-request"
      ) {
        // Popup was blocked — fall back to redirect
        try {
          await signInWithRedirect(auth, provider);
        } catch (redirectError) {
          handleAuthError(redirectError);
        }
      } else {
        handleAuthError(popupError);
      }
    }
  };

  const handleAuthError = (error) => {
    console.error("Auth error:", error.code, error.message);
    if (error.code === "auth/unauthorized-domain") {
      setAuthError(
        "⚠️ Sign-in is blocked because 'localhost' is not an authorized domain yet.\n\n" +
        "Fix: Go to Firebase Console → Authentication → Settings → Authorized Domains → Add 'localhost'.\n\n" +
        "This is a one-time setup step."
      );
    } else if (error.code === "auth/network-request-failed") {
      setAuthError("Network error — check your internet connection and try again.");
    } else {
      setAuthError(`Sign-in failed: ${error.message}`);
    }
  };

  const logout = async () => {
    setAuthError(null);
    await signOut(auth);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, authError, setAuthError, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
