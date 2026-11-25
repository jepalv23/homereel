# HomeReel Specifications

## Purpose
Keep track of the movies stored on a home NAS, external drive, or media PC:
what you own, what you've watched, and what you thought of it.

## Functional requirements
| ID  | Requirement |
|-----|-------------|
| F1  | Recursively scan a folder for video files (`.mkv .mp4 .avi .mov .m4v .wmv`). |
| F2  | Guess title and year from filenames such as `The.Matrix.1999.1080p.mkv` or `The Matrix (1999).mkv`. |
| F3  | Store movies in a local SQLite database; re-scanning must not create duplicates. |
| F4  | List and search movies by title; filter to unwatched only. |
| F5  | Mark a movie as watched and rate it 1-5. |
| F6  | Show library stats (count, watched count, total storage). |
| F7  | Remove entries whose files no longer exist (`prune`). |
| F8  | Export the library to CSV. |

## Non-functional requirements
- **Language:** Python 3.9+
- **Dependencies:** none at runtime (standard library only); `pytest` for development
- **Storage:** single SQLite file, default `~/.homereel/library.db`, override with `--db` or `HOMEREEL_DB`
- **Privacy:** fully local, no network access
- **Performance:** scanning ~10,000 files should complete in seconds

## Data model
`movies(id, title, year, path UNIQUE, size_bytes, watched, rating 1-5, added_at)`

## Architecture
```
homereel/
  scanner.py   filesystem walking + filename parsing (no database knowledge)
  db.py        all SQLite access (no printing)
  cli.py       argparse commands, glue between scanner and db
```
Each layer has one job, which keeps it easy to test and extend.

## Out of scope (v0.1)
Posters/metadata from online APIs, a web UI, TV episode tracking, playback.

## Roadmap ideas
- v0.2: fetch plot/poster from a movie API (TMDB) using an optional API key
- v0.3: small Flask web page to browse the library from any device at home
- v0.4: Java port or Java companion app for a desktop GUI
