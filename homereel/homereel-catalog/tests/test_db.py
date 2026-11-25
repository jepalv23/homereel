import pytest

from homereel import db
from homereel.scanner import MovieFile


@pytest.fixture
def conn(tmp_path):
    return db.connect(tmp_path / "test.db")


def movie(title="Up", year=2009, path="/m/up.mkv", size=100):
    return MovieFile(title, year, path, size)


def test_add_is_idempotent(conn):
    assert db.add_movie(conn, movie()) is True
    assert db.add_movie(conn, movie()) is False
    assert len(db.list_movies(conn)) == 1


def test_search_and_unwatched_filter(conn):
    db.add_movie(conn, movie("Up", 2009, "/m/up.mkv"))
    db.add_movie(conn, movie("Heat", 1995, "/m/heat.mkv"))
    db.mark_watched(conn, 1)
    assert [r["title"] for r in db.list_movies(conn, search="he")] == ["Heat"]
    assert [r["title"] for r in db.list_movies(conn, unwatched_only=True)] == ["Heat"]


def test_rating_validation(conn):
    db.add_movie(conn, movie())
    assert db.rate_movie(conn, 1, 5) is True
    with pytest.raises(ValueError):
        db.rate_movie(conn, 1, 9)


def test_prune_and_stats(conn, tmp_path):
    real = tmp_path / "real.mkv"
    real.write_bytes(b"z")
    db.add_movie(conn, movie("Real", 2000, str(real), 1))
    db.add_movie(conn, movie("Ghost", 2001, "/does/not/exist.mkv", 5))
    assert db.prune_missing(conn) == 1
    assert db.stats(conn) == {"total": 1, "watched": 0, "bytes": 1}
