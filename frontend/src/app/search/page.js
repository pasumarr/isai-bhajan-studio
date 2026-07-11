"use client";
import React, { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { usePlayer } from "../context/PlayerContext";
import API_BASE from "../utils/api";

function SearchContent() {
  const searchParams = useSearchParams();
  const { playBhajan } = usePlayer();

  const [filters, setFilters] = useState(null);
  const [query, setQuery] = useState("");
  const [deity, setDeity] = useState(searchParams.get("deity") || "");
  const [raga, setRaga] = useState("");
  const [beat, setBeat] = useState("");
  const [tempo, setTempo] = useState("");
  const [level, setLevel] = useState("");
  const [language, setLanguage] = useState("");
  const [songtags, setSongtags] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedRow, setExpandedRow] = useState(null);
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(true);
  const [searchMode, setSearchMode] = useState("standard");
  const [aiQuery, setAiQuery] = useState("");

  // Load filter options
  useEffect(() => {
    fetch(`${API_BASE}/api/filters`).then((r) => r.json()).then(setFilters).catch(console.error);
  }, []);

  const doSearch = useCallback(
    (p = 1) => {
      setLoading(true);
      setPage(p);
      const params = new URLSearchParams();
      if (query) params.append("q", query);
      if (deity) params.append("deity", deity);
      if (raga) params.append("raga", raga);
      if (beat) params.append("beat", beat);
      if (tempo) params.append("tempo", tempo);
      if (level) params.append("level", level);
      if (language) params.append("language", language);
      if (songtags) params.append("songtags", songtags);
      params.append("page", p);
      params.append("limit", 25);

      fetch(`${API_BASE}/api/search?${params}`)
        .then((r) => r.json())
        .then((data) => { setResults(data); setExpandedRow(null); })
        .catch(console.error)
        .finally(() => setLoading(false));
    },
    [query, deity, raga, beat, tempo, level, language, songtags]
  );

  // Initial search
  useEffect(() => {
    if (searchMode === "standard") {
      doSearch(1);
    } else {
      setResults(null);
      setExpandedRow(null);
    }
  }, [searchMode, doSearch]);

  const handleSubmit = (e) => { e.preventDefault(); doSearch(1); };
  const handleReset = () => {
    setQuery(""); setDeity(""); setRaga(""); setBeat("");
    setTempo(""); setLevel(""); setLanguage(""); setSongtags("");
    setTimeout(() => {
      fetch(`${API_BASE}/api/search?page=1&limit=25`)
        .then((r) => r.json()).then(setResults).catch(console.error);
    }, 0);
  };

  const handleAiSubmit = useCallback((e) => {
    if (e) e.preventDefault();
    if (!aiQuery.trim()) return;
    setLoading(true);
    fetch(`${API_BASE}/api/search/semantic?q=${encodeURIComponent(aiQuery.trim())}&limit=25`)
      .then((r) => r.json())
      .then((data) => {
        setResults({
          total: data.results.length,
          page: 1,
          total_pages: 1,
          limit: 25,
          results: data.results
        });
        setExpandedRow(null);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [aiQuery]);

  return (
    <div className="search-page">
      <h1 className="page-title">Search Bhajans</h1>

      {/* Search Mode Tabs */}
      <div className="search-mode-tabs" style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <button 
          onClick={() => setSearchMode("standard")} 
          style={{
            background: searchMode === "standard" ? "var(--accent, #ff5722)" : "rgba(255, 255, 255, 0.05)",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            padding: "8px 16px",
            fontWeight: "600",
            cursor: "pointer",
            transition: "all 0.2s"
          }}
        >
          🔍 Standard Search
        </button>
        <button 
          onClick={() => setSearchMode("ai")} 
          style={{
            background: searchMode === "ai" ? "linear-gradient(135deg, var(--accent, #ff5722), #2196f3)" : "rgba(255, 255, 255, 0.05)",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            padding: "8px 16px",
            fontWeight: "600",
            cursor: "pointer",
            transition: "all 0.2s",
            boxShadow: searchMode === "ai" ? "0 4px 15px rgba(33, 150, 243, 0.3)" : "none"
          }}
        >
          ✨ AI Semantic Search
        </button>
      </div>

      <div className="search-layout">
        {/* Standard Filter Panel */}
        {searchMode === "standard" && (
          <div className={`filter-panel ${showFilters ? "open" : "collapsed"}`}>
            <button className="filter-toggle" onClick={() => setShowFilters(!showFilters)}>
              {showFilters ? "▾ Hide Filters" : "▸ Show Filters"}
            </button>
            {showFilters && (
              <form onSubmit={handleSubmit} className="filter-form">
              <div className="filter-group full">
                <label>Lyrics / Title</label>
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search..." className="filter-input" />
              </div>
              <div className="filter-row">
                <FilterSelect label="Deity" value={deity} onChange={setDeity} options={filters?.deity} />
                <FilterSelect label="Level" value={level} onChange={setLevel} options={filters?.level} />
              </div>
              <div className="filter-row">
                <FilterSelect label="Tempo" value={tempo} onChange={setTempo} options={filters?.tempo} />
                <FilterSelect label="Beat" value={beat} onChange={setBeat} options={filters?.beat} />
              </div>
              <div className="filter-group full">
                <label>Raga</label>
                <input value={raga} onChange={(e) => setRaga(e.target.value)} placeholder="e.g. bhairavi..." className="filter-input" />
              </div>
              <div className="filter-row">
                <FilterSelect label="Language" value={language} onChange={setLanguage} options={filters?.language} />
                <FilterSelect label="Tags" value={songtags} onChange={setSongtags} options={filters?.songtags} />
              </div>
              <div className="filter-actions">
                <button type="button" onClick={handleReset} className="btn-reset">Reset</button>
                <button type="submit" className="btn-search">Search</button>
              </div>
            </form>
          )}
        </div>
        )}

        {/* AI Prompt Panel */}
        {searchMode === "ai" && (
          <div className={`filter-panel ${showFilters ? "open" : "collapsed"}`}>
            <button className="filter-toggle" onClick={() => setShowFilters(!showFilters)}>
              {showFilters ? "▾ Hide AI Search" : "▸ Show AI Search"}
            </button>
            {showFilters && (
              <form onSubmit={handleAiSubmit} className="filter-form">
                <div className="filter-group full">
                  <label style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>✨ Ask the AI Assistant</span>
                  </label>
                  <textarea 
                    value={aiQuery} 
                    onChange={(e) => setAiQuery(e.target.value)} 
                    placeholder="Describe the bhajan, mood, raga, or story (e.g. 'peaceful morning Shiva song' or 'Krishna song with Yamuna river')..." 
                    className="filter-input" 
                    rows="5"
                    style={{ resize: "none", width: "100%", padding: "10px", borderRadius: "8px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.1)", color: "#fff" }}
                  />
                </div>
                <div className="filter-actions">
                  <button type="button" onClick={() => setAiQuery("")} className="btn-reset">Clear</button>
                  <button type="submit" className="btn-search" style={{
                    background: "linear-gradient(135deg, var(--accent, #ff5722), #2196f3)",
                    boxShadow: "0 4px 15px rgba(33, 150, 243, 0.25)",
                    border: "none",
                    color: "#fff",
                    cursor: "pointer"
                  }}>
                    ✨ Search
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Results */}
        <div className="results-panel">
          {results && (
            <div className="results-header">
              <span>Showing <strong>{results.total.toLocaleString()}</strong> matching songs</span>
              <span className="results-page">Page {results.page} of {results.total_pages}</span>
            </div>
          )}

          {loading ? (
            <div className="page-loading"><div className="spinner" /><p>Searching...</p></div>
          ) : results && results.results.length > 0 ? (
            <>
              <div className="results-table-wrap">
                <table className="results-table">
                  <thead>
                    <tr><th className="col-no">No.</th><th>Song Title</th><th className="col-actions">Play</th></tr>
                  </thead>
                  <tbody>
                    {results.results.map((b, i) => (
                      <React.Fragment key={b.id}>
                        <tr className={`result-row ${expandedRow === b.id ? "expanded-header" : ""}`} onClick={() => setExpandedRow(expandedRow === b.id ? null : b.id)}>
                          <td className="col-no">{(results.page - 1) * results.limit + i + 1}</td>
                          <td className="col-title-cell">
                            <span className="title-text">{b.title}</span>
                            <span className="media-indicators">
                              {b.audio_url && <span className="mi audio" title="Audio">♫</span>}
                              {b.video_url && <span className="mi video" title="Video">▶</span>}
                            </span>
                          </td>
                          <td className="col-actions" onClick={(e) => e.stopPropagation()}>
                            <button className="play-btn" onClick={(e) => { e.stopPropagation(); playBhajan(b); }} title="Play">▶</button>
                          </td>
                        </tr>
                        {expandedRow === b.id && <ExpandedRow bhajan={b} />}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Pagination */}
              {results.total_pages > 1 && (
                <div className="pagination">
                  <button disabled={results.page <= 1} onClick={() => doSearch(results.page - 1)}>← Prev</button>
                  {Array.from({ length: Math.min(results.total_pages, 7) }, (_, i) => {
                    let p;
                    if (results.total_pages <= 7) p = i + 1;
                    else if (results.page <= 4) p = i + 1;
                    else if (results.page >= results.total_pages - 3) p = results.total_pages - 6 + i;
                    else p = results.page - 3 + i;
                    return (
                      <button key={p} className={p === results.page ? "active" : ""} onClick={() => doSearch(p)}>{p}</button>
                    );
                  })}
                  <button disabled={results.page >= results.total_pages} onClick={() => doSearch(results.page + 1)}>Next →</button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state"><div className="empty-icon">🎵</div><p>No songs found. Try adjusting your filters.</p></div>
          )}
        </div>
      </div>
    </div>
  );
}

function FilterSelect({ label, value, onChange, options }) {
  return (
    <div className="filter-group half">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="filter-input">
        <option value="">All</option>
        {options && options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function ExpandedRow({ bhajan }) {
  const { currentBhajan, isPlaying, playBhajan, togglePlay } = usePlayer();
  const isCurrent = currentBhajan?.id === bhajan.id;

  let embedUrl = "";
  if (bhajan.video_url) {
    try {
      let vid = "";
      if (bhajan.video_url.includes("youtu.be/")) vid = bhajan.video_url.split("youtu.be/")[1]?.split("?")[0];
      else if (bhajan.video_url.includes("youtube.com/watch")) vid = new URL(bhajan.video_url).searchParams.get("v");
      if (vid) embedUrl = `https://www.youtube.com/embed/${vid}`;
    } catch (e) {}
  }
  return (
    <tr className="expanded-row">
      <td colSpan="3">
        <div className="expanded-content">
          <div className="expanded-badges">
            {bhajan.deity && <span className="badge b-deity">{bhajan.deity}</span>}
            {bhajan.raga && <span className="badge b-raga">Raga: {bhajan.raga}</span>}
            {bhajan.beat && <span className="badge b-beat">Beat: {bhajan.beat}</span>}
            {bhajan.tempo && <span className="badge b-tempo">Tempo: {bhajan.tempo}</span>}
            {bhajan.level && <span className="badge b-level">{bhajan.level}</span>}
            {bhajan.language && <span className="badge b-lang">{bhajan.language}</span>}
          </div>
          <div className="expanded-split">
            <div className="expanded-lyrics">
              <h4>Lyrics</h4>
              <pre>{bhajan.title}{"\n"}{bhajan.lyrics}</pre>
            </div>
            <div className="expanded-media">
              {embedUrl && (
                <div className="video-wrap">
                  <iframe width="100%" height="220" src={embedUrl} title="Video" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
                </div>
              )}
              {bhajan.audio_url && (
                <div className="audio-wrap">
                  <h4>Audio</h4>
                  <button
                    onClick={() => isCurrent ? togglePlay() : playBhajan(bhajan)}
                    style={{
                      background: isCurrent && isPlaying ? "rgba(255, 87, 34, 0.15)" : "var(--accent, #ff5722)",
                      color: isCurrent && isPlaying ? "var(--accent, #ff5722)" : "#fff",
                      border: "1px solid var(--accent, #ff5722)",
                      borderRadius: "8px",
                      padding: "8px 16px",
                      fontSize: "0.9rem",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      fontWeight: "600",
                      transition: "all 0.2s",
                      marginTop: "0.5rem"
                    }}
                  >
                    <span>{isCurrent && isPlaying ? "⏸ Pause Audio" : "▶ Play Audio"}</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </td>
    </tr>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="page-loading"><div className="spinner" /><p>Loading search...</p></div>}>
      <SearchContent />
    </Suspense>
  );
}
