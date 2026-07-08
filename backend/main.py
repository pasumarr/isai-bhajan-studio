"""
ISai Bhajan Studio — Mark 2 FastAPI Backend
Provides REST API endpoints for bhajan search, playlists, stats, and filters.
"""

import os
import sqlite3
import math
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Database helpers (reuse existing module)
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import get_connection, init_db

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bhajans.db")

# Ensure playlist tables exist
init_db(DB_PATH)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class PlaylistCreate(BaseModel):
    name: str
    description: str = ""

class PlaylistBhajanAdd(BaseModel):
    bhajan_id: int

class PaginatedResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    results: list

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------

app = FastAPI(title="ISai Bhajan Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)

def paginate(items: list, page: int, limit: int) -> dict:
    total = len(items)
    total_pages = max(1, math.ceil(total / limit))
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "results": items[start:end],
    }

# ---------------------------------------------------------------------------
# 1. GET /api/bhajans — paginated list
# ---------------------------------------------------------------------------

@app.get("/api/bhajans")
def list_bhajans(page: int = Query(1, ge=1), limit: int = Query(25, ge=1, le=100)):
    conn = get_connection(DB_PATH)
    try:
        rows = conn.execute("SELECT * FROM bhajans ORDER BY title ASC").fetchall()
        items = [row_to_dict(r) for r in rows]
        return paginate(items, page, limit)
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# 2. GET /api/bhajans/{id}
# ---------------------------------------------------------------------------

@app.get("/api/bhajans/{bhajan_id}")
def get_bhajan(bhajan_id: int):
    conn = get_connection(DB_PATH)
    try:
        row = conn.execute("SELECT * FROM bhajans WHERE id = ?", (bhajan_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Bhajan not found")
        return row_to_dict(row)
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# 3. GET /api/search — full-text + filter search with pagination
# ---------------------------------------------------------------------------

@app.get("/api/search")
def search_bhajans(
    q: str = "",
    deity: str = "",
    raga: str = "",
    beat: str = "",
    tempo: str = "",
    level: str = "",
    language: str = "",
    songtags: str = "",
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
):
    conn = get_connection(DB_PATH)
    params: list = []

    try:
        # Build query
        if q.strip():
            try:
                sql = "SELECT b.* FROM bhajans b JOIN bhajans_fts f ON b.id = f.rowid WHERE bhajans_fts MATCH ?"
                params.append(q.strip())
            except Exception:
                sql = "SELECT b.* FROM bhajans b WHERE (b.title LIKE ? OR b.lyrics LIKE ?)"
                like = f"%{q.strip()}%"
                params.extend([like, like])
        else:
            sql = "SELECT b.* FROM bhajans b WHERE 1=1"

        # Append filters
        for col, val in [
            ("deity", deity), ("raga", raga), ("beat", beat),
            ("tempo", tempo), ("level", level), ("language", language),
            ("songtags", songtags),
        ]:
            if val.strip():
                sql += f" AND b.{col} LIKE ? COLLATE NOCASE"
                params.append(f"%{val.strip()}%")

        sql += " ORDER BY b.title ASC"

        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            # FTS5 parse error fallback
            params2: list = []
            sql2 = "SELECT b.* FROM bhajans b WHERE 1=1"
            if q.strip():
                sql2 += " AND (b.title LIKE ? OR b.lyrics LIKE ?)"
                like = f"%{q.strip()}%"
                params2.extend([like, like])
            for col, val in [
                ("deity", deity), ("raga", raga), ("beat", beat),
                ("tempo", tempo), ("level", level), ("language", language),
                ("songtags", songtags),
            ]:
                if val.strip():
                    sql2 += f" AND b.{col} LIKE ? COLLATE NOCASE"
                    params2.append(f"%{val.strip()}%")
            sql2 += " ORDER BY b.title ASC"
            rows = conn.execute(sql2, params2).fetchall()

        items = [row_to_dict(r) for r in rows]
        return paginate(items, page, limit)
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# 4. GET /api/filters — distinct values per field
# ---------------------------------------------------------------------------

@app.get("/api/filters")
def get_filters():
    conn = get_connection(DB_PATH)
    try:
        result = {}
        for col in ["deity", "raga", "beat", "tempo", "level", "language", "songtags"]:
            rows = conn.execute(
                f"SELECT DISTINCT {col} FROM bhajans WHERE {col} != '' ORDER BY {col} ASC"
            ).fetchall()
            result[col] = [r[0] for r in rows]
        return result
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# 5. GET /api/bhajans/{id}/related
# ---------------------------------------------------------------------------

@app.get("/api/bhajans/{bhajan_id}/related")
def get_related(bhajan_id: int, limit: int = Query(10, ge=1, le=50)):
    conn = get_connection(DB_PATH)
    try:
        bhajan = conn.execute("SELECT * FROM bhajans WHERE id = ?", (bhajan_id,)).fetchone()
        if not bhajan:
            raise HTTPException(404, "Bhajan not found")
        b = row_to_dict(bhajan)
        rows = conn.execute(
            "SELECT * FROM bhajans WHERE id != ? AND (deity LIKE ? OR raga LIKE ?) ORDER BY title ASC LIMIT ?",
            (bhajan_id, f"%{b['deity']}%", f"%{b['raga']}%" if b['raga'] else "__NONE__", limit),
        ).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# 6–10. Playlist CRUD
# ---------------------------------------------------------------------------

@app.post("/api/playlists")
def create_playlist(body: PlaylistCreate):
    conn = get_connection(DB_PATH)
    try:
        cur = conn.execute(
            "INSERT INTO playlists (name, description) VALUES (?, ?)",
            (body.name, body.description),
        )
        conn.commit()
        return {"id": cur.lastrowid, "name": body.name, "description": body.description}
    finally:
        conn.close()

@app.get("/api/playlists")
def list_playlists():
    conn = get_connection(DB_PATH)
    try:
        rows = conn.execute(
            """SELECT p.*, COUNT(pb.id) as bhajan_count
               FROM playlists p LEFT JOIN playlist_bhajans pb ON p.id = pb.playlist_id
               GROUP BY p.id ORDER BY p.created_at DESC"""
        ).fetchall()
        return [row_to_dict(r) for r in rows]
    finally:
        conn.close()

@app.get("/api/playlists/{playlist_id}")
def get_playlist(playlist_id: int):
    conn = get_connection(DB_PATH)
    try:
        pl = conn.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
        if not pl:
            raise HTTPException(404, "Playlist not found")
        bhajans = conn.execute(
            """SELECT b.*, pb.position, pb.added_at as playlist_added_at
               FROM playlist_bhajans pb JOIN bhajans b ON pb.bhajan_id = b.id
               WHERE pb.playlist_id = ? ORDER BY pb.position ASC""",
            (playlist_id,),
        ).fetchall()
        return {**row_to_dict(pl), "bhajans": [row_to_dict(r) for r in bhajans]}
    finally:
        conn.close()

@app.post("/api/playlists/{playlist_id}/bhajans")
def add_to_playlist(playlist_id: int, body: PlaylistBhajanAdd):
    conn = get_connection(DB_PATH)
    try:
        # Check playlist exists
        if not conn.execute("SELECT id FROM playlists WHERE id = ?", (playlist_id,)).fetchone():
            raise HTTPException(404, "Playlist not found")
        # Get next position
        row = conn.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 as next_pos FROM playlist_bhajans WHERE playlist_id = ?",
            (playlist_id,),
        ).fetchone()
        pos = row[0]
        try:
            conn.execute(
                "INSERT INTO playlist_bhajans (playlist_id, bhajan_id, position) VALUES (?, ?, ?)",
                (playlist_id, body.bhajan_id, pos),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Bhajan already in playlist")
        return {"status": "added", "position": pos}
    finally:
        conn.close()

@app.delete("/api/playlists/{playlist_id}/bhajans/{bhajan_id}")
def remove_from_playlist(playlist_id: int, bhajan_id: int):
    conn = get_connection(DB_PATH)
    try:
        cur = conn.execute(
            "DELETE FROM playlist_bhajans WHERE playlist_id = ? AND bhajan_id = ?",
            (playlist_id, bhajan_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "Entry not found")
        return {"status": "removed"}
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# 11. GET /api/stats
# ---------------------------------------------------------------------------

@app.get("/api/stats")
def get_stats():
    conn = get_connection(DB_PATH)
    try:
        total = conn.execute("SELECT COUNT(*) FROM bhajans").fetchone()[0]
        with_audio = conn.execute("SELECT COUNT(*) FROM bhajans WHERE audio_url != ''").fetchone()[0]
        with_video = conn.execute("SELECT COUNT(*) FROM bhajans WHERE video_url != ''").fetchone()[0]
        deities = conn.execute(
            "SELECT deity, COUNT(*) as count FROM bhajans WHERE deity != '' GROUP BY deity ORDER BY count DESC"
        ).fetchall()
        return {
            "total_bhajans": total,
            "with_audio": with_audio,
            "with_video": with_video,
            "deities": [{"name": r[0], "count": r[1]} for r in deities],
        }
    finally:
        conn.close()

# ---------------------------------------------------------------------------
# Run with: uvicorn main:app --reload --port 8000
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
