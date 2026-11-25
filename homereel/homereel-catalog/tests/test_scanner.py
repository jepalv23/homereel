import pytest

from homereel.scanner import parse_filename, scan_folder


@pytest.mark.parametrize(
    "stem, expected",
    [
        ("The Matrix (1999)", ("The Matrix", 1999)),
        ("The.Matrix.1999.1080p.BluRay", ("The Matrix", 1999)),
        ("Blade_Runner_2049_[2017]", ("Blade Runner 2049", 2017)),
        ("2012", ("2012", None)),
        ("Home Videos", ("Home Videos", None)),
    ],
)
def test_parse_filename(stem, expected):
    assert parse_filename(stem) == expected


def test_scan_folder_finds_only_videos(tmp_path):
    (tmp_path / "Up (2009).mkv").write_bytes(b"x" * 10)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "Heat.1995.mp4").write_bytes(b"y" * 20)
    (tmp_path / "notes.txt").write_text("ignore me")

    movies = list(scan_folder(tmp_path))
    assert [(m.title, m.year) for m in movies] == [("Up", 2009), ("Heat", 1995)] or \
           {(m.title, m.year) for m in movies} == {("Up", 2009), ("Heat", 1995)}
    assert len(movies) == 2


def test_scan_missing_folder_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        list(scan_folder(tmp_path / "nope"))
