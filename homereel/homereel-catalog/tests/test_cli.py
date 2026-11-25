from homereel.cli import main


def test_scan_then_list(tmp_path, capsys):
    (tmp_path / "Up (2009).mkv").write_bytes(b"x")
    db_file = str(tmp_path / "lib.db")

    assert main(["--db", db_file, "scan", str(tmp_path)]) == 0
    assert "1 new" in capsys.readouterr().out

    assert main(["--db", db_file, "list"]) == 0
    assert "Up (2009)" in capsys.readouterr().out


def test_scan_bad_folder_returns_error(tmp_path):
    assert main(["--db", str(tmp_path / "lib.db"), "scan", str(tmp_path / "nope")]) == 1
