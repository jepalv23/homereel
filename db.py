"""SQLite storage for the movie library."""

import os
import sqlite3
from pathlib import Path
from typing import Optional

from homereel.scanner import MovieFile

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    year       INTEGER,
    path       TEXT NOT NULL UNIQUE,
    size_bytes INTEGER NOT NULL DEFAULT 0,
    watched    INTEGER NOT NULL DEFAULT 0,
    rating     INTEGER CHECK (rating BETWEEN 1 AND 5),
    added_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def default_db_path() -> Path:
    env = os.environ.get("HOMEREEL_DB")
    return Path(env) if env else Path.home() / ".homereel" / "library.db"


def connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    db_path = Path(db_path) if db_path else default_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_movie(conn: sqlite3.Connection, movie: MovieFile) -> bool:
    """Insert a movie. Returns True if new, False if the path was already known."""
    cur = conn.execute(
        "INSERT OR IGNORE INTO movies (title, year, path, size_bytes) VALUES (?, ?, ?, ?)",
        (movie.title, movie.year, movie.path, movie.size_bytes),
    )
    conn.commit()
    return cur.rowcount == 1


def list_movies(conn, search: Optional[str] = None, unwatched_only: bool = False):
    sql = "SELECT * FROM movies WHERE 1=1"
    params: list = []
    if search:
        sql += " AND title LIKE ?"
        params.append(f"%{search}%")
    if unwatched_only:
        sql += " AND watched = 0"
    sql += " ORDER BY title COLLATE NOCASE, year"
    return conn.execute(sql, params).fetchall()


def mark_watched(conn, movie_id: int) -> bool:
    cur = conn.execute("UPDATE movies SET watched = 1 WHERE id = ?", (movie_id,))
    conn.commit()
    return cur.rowcount == 1


def rate_movie(conn, movie_id: int, rating: int) -> bool:
    if not 1 <= rating <= 5:
        raise ValueError("Rating must be between 1 and 5")
    cur = conn.execute("UPDATE movies SET rating = ? WHERE id = ?", (rating, movie_id))
    conn.commit()
    return cur.rowcount == 1


def prune_missing(conn) -> int:
    """Remove entries whose file no longer exists on disk. Returns count removed."""
    removed = 0
    for row in conn.execute("SELECT id, path FROM movies").fetchall():
        if not Path(row["path"]).exists():
            conn.execute("DELETE FROM movies WHERE id = ?", (row["id"],))
            removed += 1
    conn.commit()
    return removed


def stats(conn) -> dict:
    row = conn.execute(
        "SELECT COUNT(*) AS total, COALESCE(SUM(watched), 0) AS watched, "
        "COALESCE(SUM(size_bytes), 0) AS bytes FROM movies"
    ).fetchone()
    return {"total": row["total"], "watched": row["watched"], "bytes": row["bytes"]}
