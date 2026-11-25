"""Command-line interface for HomeReel."""

import argparse
import csv
import sys
from pathlib import Path

from homereel import __version__, db
from homereel.scanner import scan_folder


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="homereel", description="Catalog your home movie collection.")
    p.add_argument("--version", action="version", version=f"homereel {__version__}")
    p.add_argument("--db", type=Path, help="Path to the database (default: ~/.homereel/library.db)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="Scan a folder and add movies to the library")
    s.add_argument("folder", type=Path)

    l = sub.add_parser("list", help="List movies")
    l.add_argument("--search", help="Filter by title")
    l.add_argument("--unwatched", action="store_true", help="Only show unwatched movies")

    w = sub.add_parser("watch", help="Mark a movie as watched")
    w.add_argument("id", type=int)

    r = sub.add_parser("rate", help="Rate a movie 1-5")
    r.add_argument("id", type=int)
    r.add_argument("rating", type=int)

    sub.add_parser("stats", help="Show library statistics")
    sub.add_parser("prune", help="Remove entries whose files were deleted")

    e = sub.add_parser("export", help="Export the library to CSV")
    e.add_argument("output", type=Path)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    conn = db.connect(args.db)

    if args.command == "scan":
        try:
            found = new = 0
            for movie in scan_folder(args.folder):
                found += 1
                new += db.add_movie(conn, movie)
        except NotADirectoryError as err:
            print(err, file=sys.stderr)
            return 1
        print(f"Found {found} video file(s), {new} new.")

    elif args.command == "list":
        rows = db.list_movies(conn, args.search, args.unwatched)
        if not rows:
            print("No movies found.")
        for row in rows:
            year = row["year"] or "????"
            seen = "x" if row["watched"] else " "
            stars = "*" * (row["rating"] or 0)
            print(f"[{seen}] {row['id']:>4}  {row['title']} ({year})  {stars}")

    elif args.command == "watch":
        ok = db.mark_watched(conn, args.id)
        print("Marked as watched." if ok else "No movie with that id.")
        return 0 if ok else 1

    elif args.command == "rate":
        try:
            ok = db.rate_movie(conn, args.id, args.rating)
        except ValueError as err:
            print(err, file=sys.stderr)
            return 1
        print("Rated." if ok else "No movie with that id.")
        return 0 if ok else 1

    elif args.command == "stats":
        s = db.stats(conn)
        print(f"Movies:  {s['total']}")
        print(f"Watched: {s['watched']}")
        print(f"Storage: {human_size(s['bytes'])}")

    elif args.command == "prune":
        print(f"Removed {db.prune_missing(conn)} missing entr(ies).")

    elif args.command == "export":
        rows = db.list_movies(conn)
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "year", "watched", "rating", "size_bytes", "path"])
            for r in rows:
                writer.writerow([r["id"], r["title"], r["year"], r["watched"],
                                 r["rating"], r["size_bytes"], r["path"]])
        print(f"Exported {len(rows)} movie(s) to {args.output}")

    return 0
