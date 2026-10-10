from datetime import datetime

from .constants import REQUIRED_FIELDS, VALID_LEVELS
from .errors import InvalidEventError, InvalidTimestampError


class Event:
    """взять данные, проверить, что нет ошибок,
    если есть - вывести их. Превратить данные в удобный
    для программы объект"""

    def __init__(self, timestamp: datetime | None = None, level: str = '',
                source: str = '', message: str = '') -> None:
        """здесь мы говорим классу, что в нем будет лежать"""
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message

    def __repr__(self) -> str:
        """делает читаемый и понятный вывод"""
        return (f"событие (метка времени = {self.timestamp}, уровень = {self.level}, "
                f"источник = {self.source}, сообщение = {self.message})")

    def __eq__(self, other: object) -> bool:
        """обеспечивает сравнение содержимого объектов,
            а не его адреса в памяти(нужно для тестов)"""
        if not isinstance(other, Event):
            return False
        return (self.timestamp == other.timestamp and self.level == other.level
                and self.source == other.source and self.message == other.message)

    def from_dict(self, data: dict, *, line_no: int) -> "Event": 
    # *, line_no - заставляет обращаться к переменной строго по имени line_no
        """превратить словарь с данными в объект класса"""
        for field in REQUIRED_FIELDS: # проверяем, что все поля есть
            # если поля нет или оно пустое, выдаем ошибку
            if field not in data or data[field] is None:
                raise InvalidEventError(f"строка {line_no}: неверное поле {field}")

        level = data["level"]
        if not isinstance(level, str): # проверка, что верный тип данных
            # .__name__ нужно, чтобы выводилось не так <class, 'int'>, а так int
            raise InvalidEventError(f"строка {line_no}: неверный тип данных {type(level).__name__}")
        level = level.strip().upper()
        if level not in VALID_LEVELS:
            raise InvalidEventError(f"строка {line_no}: неверный уровень {data['level']}")

        source = data["source"]
        if not isinstance(source, str) or not source.strip(): 
        # .strip - удаление всех пробелов в начале и в конце строки
            raise InvalidEventError(f"строка {line_no}: source пустой или не строка")

        message = data["message"]
        if not isinstance(message, str):
            raise InvalidEventError(f"строка {line_no}: неверный тип {type(message).__name__}")

        timestamp = data["timestamp"]
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise InvalidTimestampError(f"строка {line_no}: метка времени пуста")
        try:
            # убираем пробелы по краям и пытаемся преобразовать в datetime
            ts = datetime.fromisoformat(timestamp.strip())
        except ValueError as error:
            raise InvalidTimestampError(f"строка {line_no}: формат \
                                        не соответствует ISO 8601: {timestamp}") from error

        self.timestamp = ts
        self.level = level
        self.source = source.strip()
        self.message = message

        return self
