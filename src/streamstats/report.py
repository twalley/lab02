import json

from .analysis import Analysis


def json_string(text: str) -> str:
    """записывает строку в формате JSON с экранированием особых символов"""
    return json.dumps(text, ensure_ascii=False)


def to_json(value: object, indent: int = 0) -> str:
    """Переводит объект в JSON-строку без рекурсии с отступом 4 пробела."""
    # Метод indent в json.dumps делает красивые отступы автоматически
    # Параметр indent внутри функции to_json мы учитываем через смещение
    result = json.dumps(value, ensure_ascii=False, indent=4) 
    # ensure_ascii=False нужен, чтобы сохранять не ascii символы
    if indent > 0:
        lines = result.split("\n")
        space = " " * indent
        # Сдвигаем все строки, кроме первой, на нужный начальный отступ
        return lines[0] + "\n" + "\n".join(space + line for line in lines[1:])
    return result


def report(stats: Analysis, output: str) -> None:
    """Записывает итоговый отчёт в файл JSON."""
    with open(output, "w", encoding="utf-8") as fil:
        # Получаем словарь из анализа и записываем его в файл
        fil.write(to_json(stats.to_dict()) + "\n")
