from streamstats.report import json_string, to_json


def test_json_string_escapes_special_characters() -> None:
    assert json_string('a"b\\c\nd') == '"a\\"b\\\\c\\nd"'


def test_simple_values() -> None:
    assert to_json(None) == "null"
    assert to_json(5) == "5"
    assert to_json("привет") == '"привет"'
    assert to_json({}) == "{}"
    assert to_json([]) == "[]"


def test_nested_structure_with_indents() -> None:
    value = {"всего": 2, "топ": [{"источник": "db"}], "метка": None}
    expected = (
        "{\n"
        '    "всего": 2,\n'
        '    "топ": [\n'
        "        {\n"
        '            "источник": "db"\n'
        "        }\n"
        "    ],\n"
        '    "метка": null\n'
        "}"
    )
    assert to_json(value) == expected
