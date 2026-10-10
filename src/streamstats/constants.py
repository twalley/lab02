REQUIRED_FIELDS = ("timestamp", "level", "source", "message") # обязательные поля события
VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL") # кортеж, так как менять нельзя
ERROR_LEVELS = ("ERROR", "CRITICAL")
TOP_N = 5 # сколько источников ошибок попадает в топ
EXIT_ERROR = 2
