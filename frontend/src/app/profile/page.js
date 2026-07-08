"use client";
export default function Profile() {
  return (
    <div className="coming-soon-page">
      <div className="cs-icon">👤</div>
      <h1>Your Profile</h1>
      <p>Sign in with Google or Apple to access your personalized dashboard, playlists, favorites, and contribution history.</p>
      <div className="cs-features">
        <div className="cs-feature"><span>📚</span><span>Saved playlists</span></div>
        <div className="cs-feature"><span>❤️</span><span>Favorite bhajans</span></div>
        <div className="cs-feature"><span>🏅</span><span>Contribution badges</span></div>
      </div>
    </div>
  );
}
