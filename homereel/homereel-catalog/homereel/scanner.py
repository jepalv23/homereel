"""Find video files in a folder and guess title/year from the filename."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".wmv"}
YEAR_PATTERN = re.compile(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)")


@dataclass
class MovieFile:
    title: str
    year: Optional[int]
    path: str
    size_bytes: int


def parse_filename(stem: str) -> tuple[str, Optional[int]]:
    """Turn 'The.Matrix.1999.1080p' or 'The Matrix (1999)' into ('The Matrix', 1999)."""
    matches = list(YEAR_PATTERN.finditer(stem))
    year = None
    title_part = stem
    if matches:
        last = matches[-1]
        candidate = stem[: last.start()]
        if candidate.strip(" ([-._"):  # avoid empty titles like '2012.mkv'
            title_part = candidate
            year = int(last.group(1))
    title = re.sub(r"[._]+", " ", title_part)
    title = title.strip(" ([-")
    title = re.sub(r"\s+", " ", title)
    return title, year


def scan_folder(folder: Path) -> Iterator[MovieFile]:
    """Yield a MovieFile for every video found under `folder` (recursive)."""
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
            title, year = parse_filename(path.stem)
            yield MovieFile(title, year, str(path.resolve()), path.stat().st_size)
