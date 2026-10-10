import argparse
import sys

from .analysis import Analysis
from .constants import EXIT_ERROR
from .errors import CliConfigError, StreamStatsErrors
from .parsers import parsers
from .report import report


def build_parser() -> argparse.ArgumentParser:
    """Собирает парсер аргументов командной строки и возвращает его."""
    parser = argparse.ArgumentParser(prog = "streamstats",
                                     description = "Потоковый анализатор событий из JSONL и CSV")
    sub = parser.add_subparsers(dest = "command", required = True) # создаем команды
    analyze = sub.add_parser("analyze", help = "Проанализировать файлы")
    analyze.add_argument("inputs", nargs = "+", help = "Входные файлы")
    analyze.add_argument("--format", choices = list(parsers), required = True,
                         help = "Формат входных данных")
    analyze.add_argument("--output", required = True, help = "Путь к отчету")
    analyze.add_argument("--skip-invalid", action = "store_true",
                         help = "Пропускать поврежденные строки с ошибкой")
    return parser


def run_analyze(args: argparse.Namespace) -> int:
    """Выполняет команду analyze и возвращает код выхода (0 - успех, 2 - ошибка)."""
    # функция-парсер по названию формата (argparse уже проверил, что формат есть в списке)
    parse = parsers[args.format]
    stats = Analysis()

    for file_index, path in enumerate(args.inputs, start = 1): # делаем нумерацию с 1, а не с 0
        try: # ловим ошибку от парсера или от чтения файла
            parse(path, stats, args.skip_invalid)
        except (StreamStatsErrors, OSError) as ex:
            print(f"Ошибка в файле {file_index} ({path}): {ex}", file = sys.stderr)
            return EXIT_ERROR

    try: # пишем отчет
        report(stats, args.output)
    except OSError as ex: # если не получилось записать отчет, выдаем ошибку
        print(f"Ошибка: невозможно составить отчет: {ex}", file = sys.stderr)
        return EXIT_ERROR

    return 0


def main(argv: list[str] | None = None) -> int:
    """Запускает программу и возвращает код выхода."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return run_analyze(args)

    raise CliConfigError(f"Неизвестная команда: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
