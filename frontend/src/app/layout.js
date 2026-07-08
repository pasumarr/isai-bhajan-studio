"use client";
import { PlayerProvider } from "./context/PlayerContext";
import AppShell from "./components/AppShell";
import "./globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>ISai Bhajan Studio</title>
        <meta name="description" content="Discover thousands of divine Sai bhajans with lyrics, audio, and video." />
      </head>
      <body>
        <PlayerProvider>
          <AppShell>{children}</AppShell>
        </PlayerProvider>
      </body>
    </html>
  );
}
