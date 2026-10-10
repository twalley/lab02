from datetime import datetime
import pytest
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import Event

GOOD = {"timestamp": "2024-03-01T08:00:00", "level": " info ", "source": " web ", "message": "ok"}


def test_from_dict_normalizes_level_and_source() -> None:
    event = Event().from_dict(GOOD, line_no = 2)
    assert event == Event(datetime(2024, 3, 1, 8, 0), "INFO", "web", "ok")


def test_missing_field_reports_line_number() -> None:
    data = dict(GOOD)
    del data["source"]
    with pytest.raises(InvalidEventError, match = "строка 5"):
        Event().from_dict(data, line_no = 5)


def test_unknown_level() -> None:
    with pytest.raises(InvalidEventError, match = "FATAL"):
        Event().from_dict(dict(GOOD, level = "FATAL"), line_no = 2)


def test_level_must_be_string() -> None:
    with pytest.raises(InvalidEventError, match = "int"):
        Event().from_dict(dict(GOOD, level = 5), line_no = 2)


def test_bad_timestamp() -> None:
    with pytest.raises(InvalidTimestampError, match = "ISO 8601"):
        Event().from_dict(dict(GOOD, timestamp = "вчера"), line_no = 2)


def test_repr_shows_all_fields() -> None:
    event = Event().from_dict(GOOD, line_no = 2)
    assert repr(event) == ("событие (метка времени = 2024-03-01 08:00:00, уровень = INFO, "
                           "источник = web, сообщение = ok)")
