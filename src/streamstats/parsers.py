from .analysis import Analysis
from .errors import InvalidEventError, StreamStatsErrors
from .models import Event


def war(path: str, message: str) -> None:
    """отдельная функция, чтобы не писать одно и тоже много раз"""
    print(f"WARNING: {path}: {message}")

def handle_bad_line(error: StreamStatsErrors, path: str, stats: Analysis, 
                    skip_invalid: bool) -> None:
    """нужно для того, чтобы человек при вводе в консоли мог выбрать формат чтения,
       если нужно закончить программу при пустой сроке не надо прописывать --skip-invalid,
       если же нужна более мягкая проверка, т. е. допускается возможность прокуска строки,
       высвечивается предупреждение и программа рабтает дальше"""
    if not skip_invalid:
        raise error
    war(path, str(error))
    stats.mark_skipp()





def split_csv_line(line: str, line_no: int) -> list[str]:
    """используем после readline() для разбивки строки на значения
       под столбцами, так же учитываем сложные случаи, например,
       "kfmdk,dfjbn" запитая является частью элемента,
        тройные кавычки считаем за одинарные"""
    values = []
    current = "" # значение, которое собираем сейчас
    in_quotes = False # находимся ли внутри кавычек
    prev = "" # предыдущий символ
    for char in line:
        if char == '"':
            if in_quotes:
                in_quotes = False # кавычки закрылись
            else:
                if prev == '"': # кавычка сразу после закрытой - это "" внутри значения
                    current += '"'
                in_quotes = True # кавычки открылись
        elif char == "," and not in_quotes:
            values.append(current) # запятая вне кавычек - значение закончилось
            current = ""
        else:
            current += char
        prev = char
    if in_quotes:
        raise InvalidEventError(f"строка {line_no}: незакрытая кавычка")
    values.append(current) # последнее значение (после него запятой нет)
    return values


def pars_csv(path: str, stats: Analysis, skip_invalid: bool = False) -> None:
    """читаем csv файл построкам"""
    # utf-8-sig - если файл из Excel (убирает невидимый символ BOM)
    with open(path, encoding = "utf-8-sig") as fil:
        header = None # названия колонок из первой строки
        line_no = 0 # номер текущей строки файла
        
        while True: 
        # бесконечный цикл, который идет по файлу до тех пор, пока он не закончится
            line = fil.readline() # читаем одну строку
            
            if line == "": # пустая строка - файл закончился
                break
            line_no += 1
            
            if line.strip() == "": # пустые строки пропускаем, это не ошибка
                continue
            
            try:
                values = split_csv_line(line.rstrip("\n"), line_no) # .rstrip отчищаем \n справа
                
                if header is None:
                    header = [name.strip() for name in values]
                    # если вместо заголовков какая-то фигня
                    if "timestamp" not in header or "level" not in header:
                        raise InvalidEventError(
                            f"строка {line_no}: неверный формат CSV: "
                            f"отсутствуют обязательные заголовки"
                        )
                    continue

                if header is None: # первая непустая строка - заголовок
                    header = [name.strip() for name in values]
                    continue
                
                if len(values) != len(header):
                    raise InvalidEventError(f"строка {line_no}: должно быть {len(header)} значений,\
                                             получено {len(values)}")
                row = {}
                
                for i in range(len(header)): # собираем словарь колонка: значение
                    row[header[i]] = values[i]
                
                event = Event().from_dict(row, line_no = line_no)
            
            except StreamStatsErrors as ex:
                handle_bad_line(ex, path, stats, skip_invalid)
                continue
            
            stats.add_event(event)






def split_json_pairs(text: str, line_no: int) -> list[str]:
    """получает строку, разбивает ее на 'ключ: значение' по запятым,
        обработка сложных случаев, например, запятая внутри кавычек не является разделителем"""
    pairs = []
    current = ""
    in_quotes = False # внутри строки в кавычках
    escaped = False # предыдущий символ был \ (значит эта кавычка - часть текста)
    
    for char in text:
        
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            in_quotes = not in_quotes # кавычка открывает или закрывает строку
        
        if char == "," and not in_quotes:
            pairs.append(current) # запятая вне кавычек - пара закончилась
            current = ""
        else:
            current += char

    if in_quotes:
        raise InvalidEventError(f"строка {line_no}: неверный JSON: незакрытая кавычка")
    pairs.append(current)
    return pairs


def unescape(text: str) -> str:
    """здесь убираем экранирование со строки, т.е.
         \\" -> "   \\\\ -> \\   \\n -> перевод строки"""
    result = ""
    escaped = False
    for char in text:
        if escaped: # символ после \
            if char == "n":
                result += "\n"
            elif char == "t":
                result += "\t"
            else:
                result += char
            escaped = False
        elif char == "\\":
            escaped = True
        else:
            result += char
    return result


def json_value(text: str, line_no: int) -> object:
    """нужно для перевода текста после двоеточия на язык питона (int, str, тд)"""
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return unescape(text[1:-1]) # убираем кавычки по краям строки
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text.lstrip("-").isdigit(): # целое число (например, 42 или -7)
        return int(text)
    if text.lstrip("-").replace(".", "", 1).isdigit(): 
    # дробное число (например, 2.5), проверяем с помощью удаления первой запятой
        return float(text)
    raise InvalidEventError(f"строка {line_no}: неверный JSON: непонятное значение {text}")


def parse_json_line(line: str, line_no: int) -> dict:
    """нужно для разбивки на {ключ: значение} и преобразования в словарь"""
    
    if not line.startswith("{") or not line.endswith("}"):
        raise InvalidEventError(f"строка {line_no}: неверный JSON: нужен объект в фигурных скобках")
    
    inside = line[1:-1].strip() # все, что внутри {}
    data: dict[str, object] = {}
    if inside == "": # пустой объект {}
        return data
    
    for pair in split_json_pairs(inside, line_no):
        key, colon, value = pair.partition(":") # делим по первому двоеточию
        key = key.strip()
        
        if colon == "" or len(key) < 2 or not key.startswith('"') or not key.endswith('"'):
            raise InvalidEventError(f'строка {line_no}: неверный JSON: \
                                    должно быть "ключ": значение')
        
        data[key[1:-1]] = json_value(value.strip(), line_no)
    return data


def pars_jsonl(path: str, stats: Analysis, skip_invalid: bool = False) -> None:
    """читает по одной строке """
    with open(path, encoding = "utf-8") as fil:
        line_no = 0 # номер текущей строки файла
        
        while True:
            line = fil.readline() # читаем одну строку
            
            if line == "": # пустая строка - файл закончился
                break
            
            line_no += 1
            line = line.strip() # убираем пробелы и \n по краям
            if not line: # если строка пустая пропускаем ее, т.к. это не ошибка
                continue
            
            try:
                data = parse_json_line(line, line_no)
                event = Event().from_dict(data, line_no = line_no)
            except StreamStatsErrors as ex:
                handle_bad_line(ex, path, stats, skip_invalid)
                continue
            
            stats.add_event(event)


# определяем формат и соответственно какую функцию использовать
parsers = {"csv": pars_csv, "jsonl": pars_jsonl}