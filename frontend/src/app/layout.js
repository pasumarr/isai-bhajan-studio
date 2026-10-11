"use client";
import { PlayerProvider } from "./context/PlayerContext";
import AppShell from "./components/AppShell";
import { AuthProvider } from "./context/AuthContext";
import { FavoritesProvider } from "./context/FavoritesContext";
import "./globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>ISai Bhajan Studio</title>
        <meta name="description" content="Discover thousands of divine Sai bhajans with lyrics, audio, and video." />
      </head>
      <body>
        <AuthProvider>
          <FavoritesProvider>
            <PlayerProvider>
              <AppShell>{children}</AppShell>
            </PlayerProvider>
          </FavoritesProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
