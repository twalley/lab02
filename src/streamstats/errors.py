class StreamStatsErrors(Exception):
    """Базовое исключение пакета"""


class UnsupportedFormatError(StreamStatsErrors):
    """Неверный формат данных"""


class InvalidEventError(StreamStatsErrors):
    """Событие не соответствует модели (пустой source, нет поля и др)"""


class InvalidTimestampError(StreamStatsErrors):
    """Метка времени не соответствует формату ISO 8601"""


class CliConfigError(StreamStatsErrors):
    """Неверные аргументы командной строки"""
