from pathlib import Path
import pytest
from streamstats.__main__ import main

HEADER = "timestamp,level,source,message\n"


def write(path: Path, text: str) -> str:
    """Записывает файл и возвращает путь строкой"""
    path.write_text(text, encoding = "utf-8")
    return str(path)


def test_two_files_go_into_one_report(tmp_path: Path) -> None:
    first = write(tmp_path / "a.csv", HEADER + "2024-03-01T08:00:00,INFO,web,ok\n")
    second = write(tmp_path / "b.csv", HEADER + "2024-03-02T08:00:00,ERROR,db,\"сбой, повтор\"\n")
    output = tmp_path / "report.json"
    code = main(["analyze", first, second, "--format", "csv", "--output", str(output)])
    text = output.read_text(encoding = "utf-8")
    assert code == 0
    assert '"всего событий": 2' in text
    assert '"последняя временная метка": "2024-03-02T08:00:00"' in text


def test_bad_line_stops_with_code_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = write(tmp_path / "a.csv", HEADER + "вчера,INFO,web,ok\n")
    code = main(["analyze", source, "--format", "csv", "--output", str(tmp_path / "r.json")])
    assert code == 2
    assert "Ошибка в файле 1" in capsys.readouterr().err
    assert not (tmp_path / "r.json").exists()


def test_skip_invalid_writes_report(tmp_path: Path) -> None:
    source = write(tmp_path / "a.jsonl", '{"broken"\n')
    output = tmp_path / "r.json"
    code = main(["analyze", source, "--format", "jsonl", "--output", str(output), "--skip-invalid"])
    assert code == 0
    assert '"пропущенные строки": 1' in output.read_text(encoding = "utf-8")


def test_missing_file_gives_code_2(tmp_path: Path) -> None:
    code = main(["analyze", str(tmp_path / "нет.csv"), "--format", "csv",
                 "--output", str(tmp_path / "r.json")])
    assert code == 2


def test_unknown_format_is_rejected_by_argparse(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["analyze", "a.xml", "--format", "xml", "--output", str(tmp_path / "r.json")])
    assert exit_info.value.code == 2
