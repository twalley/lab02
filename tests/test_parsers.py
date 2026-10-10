from pathlib import Path
import pytest
from streamstats.analysis import Analysis
from streamstats.errors import InvalidEventError
from streamstats.parsers import pars_csv, pars_jsonl, parse_json_line, parsers, split_csv_line

HEADER = "timestamp,level,source,message\n"
GOOD_JSON = ('{"timestamp": "2024-03-01T08:00:00", "level": "INFO", '
             '"source": "web", "message": "ok"}')


def test_split_simple_line() -> None:
    assert split_csv_line("a,b,c", 1) == ["a", "b", "c"]


def test_split_comma_and_quotes_inside_quotes() -> None:
    line = 'x,"Запрос обработан, ""200 OK"""'
    assert split_csv_line(line, 1) == ["x", 'Запрос обработан, "200 OK"']


def test_split_empty_values() -> None:
    assert split_csv_line(',,""', 1) == ["", "", ""]


def test_split_unclosed_quote() -> None:
    with pytest.raises(InvalidEventError, match = "строка 3"):
        split_csv_line('a,"b', 3)


def test_json_line_with_all_value_types() -> None:
    line = '{"s": "a, b: c", "n": 5, "f": 2.5, "t": true, "no": false, "x": null}'
    assert parse_json_line(line, 1) == {"s": "a, b: c", "n": 5, "f": 2.5, "t": True,
                                        "no": False, "x": None}


def test_json_escapes() -> None:
    line = '{"a": "кав\\"ычка, слеш \\\\ и\\nперенос"}'
    assert parse_json_line(line, 1) == {"a": 'кав"ычка, слеш \\ и\nперенос'}


def test_json_empty_object() -> None:
    assert parse_json_line("{}", 1) == {}


def test_broken_json() -> None:
    broken = ['{"a": 1,}', '{"a" 1}', "{a: 1}", '{"a": [1]}', '{"a": "x}', "5",
              '{"level": "INFO", сломано']
    for line in broken: # каждая битая строка - ошибка с номером строки
        with pytest.raises(InvalidEventError, match = "строка 7"):
            parse_json_line(line, 7)


def test_csv_file(tmp_path: Path) -> None:
    file = tmp_path / "log.csv"
    lines = ["2024-03-01T08:00:00,INFO,web,ok", "", "2024-03-01T09:00:00,ERROR,db,fail"]
    file.write_text(HEADER + "\n".join(lines) + "\n", encoding = "utf-8")
    stats = Analysis()
    pars_csv(str(file), stats)
    assert stats.total_event == 2
    assert stats.err_sources == {"db": 1}


def test_csv_wrong_number_of_values(tmp_path: Path) -> None:
    file = tmp_path / "log.csv"
    file.write_text(HEADER + "2024-03-01T08:00:00,INFO,web\n", encoding = "utf-8")
    with pytest.raises(InvalidEventError, match = "строка 2"):
        pars_csv(str(file), Analysis())


def test_jsonl_bad_line_stops_reading(tmp_path: Path) -> None:
    file = tmp_path / "log.jsonl"
    file.write_text((GOOD_JSON + "\n") * 6 + "{сломано\n", encoding = "utf-8")
    with pytest.raises(InvalidEventError, match = "строка 7"):
        pars_jsonl(str(file), Analysis())


def test_jsonl_skip_invalid_counts_skipped(tmp_path: Path,
                                           capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "log.jsonl"
    file.write_text(GOOD_JSON + "\n{сломано\n" + GOOD_JSON + "\n", encoding = "utf-8")
    stats = Analysis()
    pars_jsonl(str(file), stats, skip_invalid = True)
    assert stats.total_event == 2
    assert stats.skipp_invalid == 1
    assert "WARNING" in capsys.readouterr().out


def test_parsers_registry() -> None:
    assert parsers["csv"] is pars_csv
    assert parsers["jsonl"] is pars_jsonl
