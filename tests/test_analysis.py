from datetime import datetime

from streamstats.analysis import Analysis
from streamstats.models import Event


def make_event(hour: int, level: str, source: str) -> Event:
    """Создаёт событие 1 марта 2024 года в заданный час"""
    return Event(datetime(2024, 3, 1, hour, 0), level, source, "сообщение")


def test_counts_levels_and_sources() -> None:
    stats = Analysis()
    stats.add_event(make_event(8, "INFO", "web"))
    stats.add_event(make_event(9, "ERROR", "db"))
    stats.add_event(make_event(10, "ERROR", "db"))
    report = stats.to_dict()
    assert report["всего событий"] == 3
    assert report["уровни"]["ERROR"] == 2
    assert report["уровни"]["DEBUG"] == 0
    assert report["источники"] == {"web": 1, "db": 2}


def test_first_and_last_timestamp_in_any_order() -> None:
    stats = Analysis()
    for hour in (10, 7, 12):
        stats.add_event(make_event(hour, "INFO", "web"))
    report = stats.to_dict()
    assert report["первая временная метка"] == "2024-03-01T07:00:00"
    assert report["последняя временная метка"] == "2024-03-01T12:00:00"


def test_top_is_sorted_by_count_then_alphabet_and_limited() -> None:
    stats = Analysis()
    for source in ("f", "b", "e", "a", "d", "c"):
        stats.add_event(make_event(8, "ERROR", source))
    stats.add_event(make_event(9, "CRITICAL", "z"))
    stats.add_event(make_event(9, "CRITICAL", "z"))
    top = [item["источник"] for item in stats.to_dict()["топ 5 ошибок источников"]]
    assert top == ["z", "a", "b", "c", "d"]


def test_empty_statistics() -> None:
    report = Analysis().to_dict()
    assert report["всего событий"] == 0
    assert report["первая временная метка"] is None
    assert report["топ 5 ошибок источников"] == []


def test_event_without_timestamp_is_counted() -> None:
    stats = Analysis()
    stats.add_event(Event(level = "INFO", source = "web"))
    report = stats.to_dict()
    assert report["всего событий"] == 1
    assert report["первая временная метка"] is None
