# HomeReel 🎬

A tiny command-line catalog for your home movie collection. Point it at the
folder on your NAS, external drive, or media PC, and it builds a searchable
library where you can track what you've watched and rate what you liked.

![CI](https://github.com/jepalv23/homereel/actions/workflows/ci.yml/badge.svg)

## Features
- Scans folders recursively for video files
- Guesses title and year from messy filenames (`The.Matrix.1999.1080p.mkv` → *The Matrix (1999)*)
- Stores everything in a local SQLite file, so there's no server and no cloud
- Search, filter unwatched, mark watched, rate 1-5
- Library stats and CSV export
- Zero runtime dependencies

## Requirements
- Python 3.9 or newer

## Installation
```bash
git clone https://github.com/YOUR-USERNAME/homereel.git
cd homereel
pip install -e .
```

## Usage
```bash
# Add movies from a folder (safe to run again; no duplicates)
homereel scan /mnt/nas/movies

# See what you have
homereel list
homereel list --search matrix
homereel list --unwatched

# Track your viewing
homereel watch 3
homereel rate 3 5

# Housekeeping
homereel stats
homereel prune                 # drop entries for deleted files
homereel export movies.csv
```

Example output:
```
$ homereel list
[x]    1  Heat (1995)  ****
[ ]    2  The Matrix (1999)
[ ]    3  Up (2009)
```

Use a different database file with `--db my.db` or the `HOMEREEL_DB` environment variable.

You can also run it without installing: `python -m homereel list`.

## Running the tests
```bash
pip install -e ".[dev]"
pytest
```

## Project layout
```
homereel/      application code (scanner, db, cli)
tests/         pytest tests
SPECS.md       requirements, data model, roadmap
```

## Contributing
Issues and pull requests are welcome. Please add a test for any new behavior.




