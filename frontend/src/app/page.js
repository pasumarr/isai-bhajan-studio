"use client";

import React, { useState, useEffect } from "react";

export default function Home() {
  const [bhajans, setBhajans] = useState([]);
  const [query, setQuery] = useState("");
  const [deity, setDeity] = useState("");
  const [raga, setRaga] = useState("");
  const [beat, setBeat] = useState("");
  const [tempo, setTempo] = useState("");
  const [level, setLevel] = useState("");
  const [language, setLanguage] = useState("");
  const [songtags, setSongtags] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedRow, setExpandedRow] = useState(null);

  const fetchBhajans = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (query) params.append("q", query);
      if (deity) params.append("deity", deity);
      if (raga) params.append("raga", raga);
      if (beat) params.append("beat", beat);
      if (tempo) params.append("tempo", tempo);
      if (level) params.append("level", level);
      if (language) params.append("language", language);
      if (songtags) params.append("songtags", songtags);

      const res = await fetch(`/api/search?${params.toString()}`);
      const data = await res.json();
      setBhajans(data);
    } catch (error) {
      console.error("Error fetching bhajans:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBhajans();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    setExpandedRow(null);
    fetchBhajans();
  };

  const handleReset = () => {
    setQuery("");
    setDeity("");
    setRaga("");
    setBeat("");
    setTempo("");
    setLevel("");
    setLanguage("");
    setSongtags("");
    setExpandedRow(null);
    // Fetch with cleared state on next tick
    setTimeout(() => {
      const params = new URLSearchParams();
      fetch(`/api/search?${params.toString()}`)
        .then(res => res.json())
        .then(data => { setBhajans(data); setLoading(false); });
    }, 0);
  };

  const toggleRow = (id) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  return (
    <>
      <header className="site-header">
        <div className="header-content">
          <h1>ISai Bhajan Studio</h1>
          <h2>Devotional Song Collection</h2>
        </div>
      </header>

      <div className="main-container">
        <div className="page-header-wrapper">
          <h2 className="page-header">Devotional Songs</h2>
        </div>

        <div className="content-layout">
          {/* Search Criteria Panel - Left Sidebar */}
          <div className="search-criteria-panel">
            <form onSubmit={handleSearch} className="search-form">
              <div className="form-group full-width">
                <label className="form-label primary">Lyrics</label>
                <input
                  type="text"
                  placeholder="Search lyrics or title..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="form-input"
                />
              </div>

              <div className="advanced-filters">
                <div className="form-group half-width">
                  <label className="form-label">Deity</label>
                  <select value={deity} onChange={(e) => setDeity(e.target.value)} className="form-input">
                    <option value=""></option>
                    <option value="allah">Allah</option>
                    <option value="anjaneya">Anjaneya</option>
                    <option value="ayyappa">Ayyappa</option>
                    <option value="buddha">Buddha</option>
                    <option value="devi">Devi</option>
                    <option value="ganesha">Ganesha</option>
                    <option value="gayathri">Gayathri</option>
                    <option value="guru">Guru</option>
                    <option value="jehovah">Jehovah</option>
                    <option value="jesus">Jesus</option>
                    <option value="krishna">Krishna</option>
                    <option value="narasimha">Narasimha</option>
                    <option value="narayana">Narayana</option>
                    <option value="rama">Rama</option>
                    <option value="sai">Sai</option>
                    <option value="sarva dharma">Sarva Dharma</option>
                    <option value="shiva">Shiva</option>
                    <option value="subrahmanya">Subrahmanya</option>
                    <option value="surya">Surya</option>
                    <option value="vittala">Vittala</option>
                  </select>
                </div>

                <div className="form-group half-width">
                  <label className="form-label">Level</label>
                  <select value={level} onChange={(e) => setLevel(e.target.value)} className="form-input">
                    <option value=""></option>
                    <option value="simple">Simple</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div className="form-group half-width">
                  <label className="form-label">Tempo</label>
                  <select value={tempo} onChange={(e) => setTempo(e.target.value)} className="form-input">
                    <option value=""></option>
                    <option value="slow">Slow</option>
                    <option value="medium slow">Medium Slow</option>
                    <option value="medium">Medium</option>
                    <option value="medium fast">Medium Fast</option>
                    <option value="fast">Fast</option>
                  </select>
                </div>

                <div className="form-group half-width">
                  <label className="form-label">Beat</label>
                  <select value={beat} onChange={(e) => setBeat(e.target.value)} className="form-input">
                    <option value=""></option>
                    <option value="6 beat / dadra">6 Beat / Dadra</option>
                    <option value="7 beat / rupak / misrachapu">7 Beat / Rupak / Misrachapu</option>
                    <option value="8 beat / keherwa / adi">8 Beat / Keherwa / Adi</option>
                    <option value="10 beat / jhap taal">10 Beat / Jhap Taal</option>
                  </select>
                </div>

                <div className="form-group full-width">
                  <label className="form-label">Raga</label>
                  <input
                    type="text"
                    placeholder="e.g. bhairavi, kafi..."
                    value={raga}
                    onChange={(e) => setRaga(e.target.value)}
                    className="form-input"
                  />
                </div>

                <div className="form-group half-width">
                  <label className="form-label">Language</label>
                  <select value={language} onChange={(e) => setLanguage(e.target.value)} className="form-input">
                    <option value=""></option>
                    <option value="arabic">Arabic</option>
                    <option value="bengali">Bengali</option>
                    <option value="english">English</option>
                    <option value="french">French</option>
                    <option value="hawaiian">Hawaiian</option>
                    <option value="hebrew">Hebrew</option>
                    <option value="japanese">Japanese</option>
                    <option value="kannada">Kannada</option>
                    <option value="marathi">Marathi</option>
                    <option value="portuguese">Portuguese</option>
                    <option value="punjabi">Punjabi</option>
                    <option value="russian">Russian</option>
                    <option value="sanskrit / hindi">Sanskrit / Hindi</option>
                    <option value="spanish">Spanish</option>
                    <option value="tamil">Tamil</option>
                    <option value="telugu">Telugu</option>
                    <option value="multi-lingual">Multi-Lingual</option>
                  </select>
                </div>

                <div className="form-group half-width">
                  <label className="form-label">Song Tags</label>
                  <select value={songtags} onChange={(e) => setSongtags(e.target.value)} className="form-input">
                    <option value=""></option>
                    <option value="arathi">Arathi</option>
                    <option value="carols">Carols</option>
                    <option value="folk">Folk</option>
                    <option value="golden voice">Golden Voice</option>
                    <option value="instrumental">Instrumental</option>
                    <option value="karaoke">Karaoke</option>
                    <option value="lead-music">Lead Music</option>
                    <option value="multi-lingual">Multi-Lingual</option>
                    <option value="prayers">Prayers</option>
                    <option value="sheet-music">Sheet Music</option>
                    <option value="tutorial">Tutorial</option>
                  </select>
                </div>
              </div>

              <div className="form-actions">
                <button type="button" onClick={handleReset} className="btn btn-danger">Reset</button>
                <button type="submit" className="btn btn-primary">Search</button>
              </div>
            </form>
          </div>

          {/* Search Results Panel - Right Main Area */}
          <div className="search-results-panel">
            <div className="results-summary">
              Number of Matching Songs: <span className="results-count">{bhajans.length}</span>
            </div>

            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                <p>Loading divine rhythms...</p>
              </div>
            ) : bhajans.length > 0 ? (
              <div className="table-responsive">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th className="col-no">No.</th>
                      <th className="col-title">Song Title</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bhajans.map((bhajan, index) => {
                      let youtubeEmbedUrl = "";
                      if (bhajan.video_url) {
                        try {
                          let videoId = "";
                          if (bhajan.video_url.includes("youtu.be/")) {
                            videoId = bhajan.video_url.split("youtu.be/")[1]?.split("?")[0];
                          } else if (bhajan.video_url.includes("youtube.com/watch")) {
                            const urlObj = new URL(bhajan.video_url);
                            videoId = urlObj.searchParams.get("v");
                          }
                          if (videoId) {
                            youtubeEmbedUrl = `https://www.youtube.com/embed/${videoId}`;
                          }
                        } catch (e) {}
                      }

                      return (
                        <React.Fragment key={bhajan.id}>
                          <tr
                            className={`result-row ${expandedRow === bhajan.id ? 'expanded-header' : ''}`}
                            onClick={() => toggleRow(bhajan.id)}
                          >
                            <td className="col-no text-center">{index + 1}</td>
                            <td className="col-title">
                              <div className="title-text">{bhajan.title}</div>
                              <div className="title-badges">
                                {bhajan.audio_url && <span className="mini-badge audio-badge" title="Audio available">♫</span>}
                                {bhajan.video_url && <span className="mini-badge video-badge" title="Video available">▶</span>}
                              </div>
                              <div className="expand-icon">{expandedRow === bhajan.id ? '−' : '+'}</div>
                            </td>
                          </tr>
                          {expandedRow === bhajan.id && (
                            <tr className="expanded-details-row">
                              <td colSpan="2">
                                <div className="expanded-content">
                                  <div className="metadata-badges">
                                    {bhajan.deity && <span className="badge badge-deity">{bhajan.deity}</span>}
                                    {bhajan.raga && <span className="badge badge-raga">Raga: {bhajan.raga}</span>}
                                    {bhajan.beat && <span className="badge badge-beat">Beat: {bhajan.beat}</span>}
                                    {bhajan.tempo && <span className="badge badge-tempo">Tempo: {bhajan.tempo}</span>}
                                    {bhajan.level && <span className="badge badge-level">Level: {bhajan.level}</span>}
                                    {bhajan.language && <span className="badge badge-language">Lang: {bhajan.language}</span>}
                                  </div>

                                  <div className="content-split-layout">
                                    <div className="lyrics-box">
                                      <h4>Lyrics</h4>
                                      <pre>{bhajan.lyrics}</pre>
                                    </div>

                                    <div className="media-box">
                                      {youtubeEmbedUrl && (
                                        <div className="video-player-wrapper">
                                          <iframe
                                            width="100%"
                                            height="250"
                                            src={youtubeEmbedUrl}
                                            title="YouTube video player"
                                            frameBorder="0"
                                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                                            allowFullScreen>
                                          </iframe>
                                        </div>
                                      )}
                                      {bhajan.audio_url && (
                                        <div className="audio-player-wrapper">
                                          <h4>Audio</h4>
                                          <audio controls src={bhajan.audio_url} className="custom-audio"></audio>
                                        </div>
                                      )}
                                      {!youtubeEmbedUrl && !bhajan.audio_url && (
                                        <div className="no-media">
                                          <p>No media available for this bhajan.</p>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🎵</div>
                <p>Sorry, no songs match your search. Please try changing the search criteria.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
