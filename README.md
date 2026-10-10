Лабораторная работа 2. Потоковый анализатор файлов
Сычева Виктория Сергеевна, М8О-101БВ-26

Пакет streamstats читает события из CSV и JSONL построчно и сохраняет JSON-отчёт: общее число событий, число событий каждого уровня и каждого источника, топ-5 источников ошибок (ERROR/CRITICAL), первая и последняя временная метка, число пропущенных строк.
Статистика нескольких файлов складывается в один отчёт.


Структура

text
src/streamstats/
  __init__.py   - делает папку пакетом
  __main__.py   - командная строка (argparse) и коды выхода
  constants.py  - уровни, обязательные поля, TOP_N, код ошибки
  errors.py     - StreamStatsErrors и её наследники
  models.py     - класс Event и проверка строки Event().from_dict()
  parsers.py    - разбор CSV и JSONL по одной строке, реестр parsers
  analysis.py   - класс Analysis (счётчики)
  report.py     - запись отчёта в JSON
tests/
  test_models.py, test_parsers.py, test_analysis.py, test_report.py - unit-тесты
  test_cli.py   - интеграционные тесты всей программы во временном каталоге


Установка и запуск

Командная строка:
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m streamstats analyze a.csv b.csv --format csv --output report.json
python -m streamstats analyze log.jsonl --format jsonl --output report.json --skip-invalid


Ошибочные строки

- По умолчанию: чтение останавливается, в поток ошибок пишется номер файла и строки, код выхода 2.
- --skip-invalid: строка пропускается, печатается предупреждение WARNING: файл: строка N: ..., в отчёте увеличивается пропущенные строки.

Память

Парсеры читают файл по одной строке (fil.readline() в цикле while), сразу проверяют её и добавляют событие (строку) в Analysis. read() и readlines() не используются. Analysis хранит только
счётчики, а не события, поэтому память не зависит от размера файла.

Ограничения

- CSV: перенос строки внутри значения в кавычках не поддерживается.
- JSONL: поддерживается плоский объект (строки, числа, true, false, null); коды \uXXXX в строках не раскрываются, в ключах не должно быть двоеточия.
- Даты с часовым поясом и без него в одном отчёте сравнить нельзя.

Проверка

Командная строка:
pip install pytest ruff mypy
python -m pytest
ruff check .
mypy src

