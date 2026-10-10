from datetime import datetime

from .constants import ERROR_LEVELS, TOP_N, VALID_LEVELS
from .models import Event


class Analysis:
    """нужен для подсчета статистики и в дальнейшем удобного вывода ее"""

    def __init__(self) -> None:
        """говорим классу, что в нем будет лежать"""
        
        # общее колличество событий
        self.total_event: int = 0
        
        # все уровни сразу с нулями, для каждого уровня создается пара (уровень: 0)
        self.levels: dict[str, int] = {lvl: 0 for lvl in VALID_LEVELS}
        
        # источник: количество; пустой, т.к. источники заранее неизвестны
        self.sources: dict[str, int] = {}
        
        # только для ERROR и CRITICAL, нужен для топа источников ошибок
        self.err_sources: dict[str, int] = {}
        
        # самая ранняя и самая поздняя метка времени; до первого события - None
        self.first_timestamp: datetime | None = None
        self.last_timestamp: datetime | None = None
        
        # счетчик пропущенных строк
        self.skipp_invalid: int = 0 

    
    def add_event(self, event: Event) -> None:
        """для добавления одного события (строки)"""
        self.total_event += 1
        self.levels[event.level] += 1
        # берем значение по ключу, если его нет, то 0
        self.sources[event.source] = self.sources.get(event.source, 0) + 1

        if event.level in ERROR_LEVELS:
            self.err_sources[event.source] = self.err_sources.get(event.source, 0) + 1

        ts = event.timestamp
        if ts is None: # у события без метки времени сравнивать нечего
            return
        if self.first_timestamp is None or ts < self.first_timestamp: # обновление первой метки
            self.first_timestamp = ts

        if self.last_timestamp is None or ts > self.last_timestamp: # обновление последней метки
            self.last_timestamp = ts

    
    def mark_skipp(self) -> None:
        """нужно для подсчета пропущенных строк"""
        self.skipp_invalid += 1

    
    def to_dict(self) -> dict:
        """завершает работу, собирая все в словарь"""
        # сортируем по убыванию числа ошибок, при равенстве - по алфавиту, и берем первые TOP_N
        top = sorted(self.err_sources.items(), key = lambda x: (-x[1], x[0]))[:TOP_N]
        first = self.first_timestamp.isoformat() if self.first_timestamp else None
        last = self.last_timestamp.isoformat() if self.last_timestamp else None
        return {"всего событий": self.total_event,
                "уровни": self.levels,
                "источники": self.sources,
                "топ 5 ошибок источников": [{"источник": src, "количество ошибок": err}
                                            for src, err in top],
                "первая временная метка": first,
                "последняя временная метка": last,
                "пропущенные строки": self.skipp_invalid}
