"""v 0.200"""
#добавлен вывод разделителя
import logging

# Настройка логирования
def configure_logging(path2log):
    """Настройка логирования."""
    # Очистка предыдущих настроек логирования
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Настройка нового логгера
    logging.basicConfig(
        filename=path2log,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    
    # Добавление разделителя для новой сессии
    separator = "\n" + 30 * "-" + "\nnew log" + 30 * "-" + "\n"
    logging.info(separator.strip())  # Запись разделителя в лог

# Функция логирования
def log_v2(log_data, log_type="info"):
    """
    Логирование с выводом в консоль и файл.
    :param log_data: Текст для логирования.
    :param log_type: Тип лога ('info', 'error', 'debug').
    """
    print(log_data)  # Вывод в консоль
    if log_type == "info":
        logging.info(log_data)  # Запись в лог как INFO
    elif log_type == "error":
        logging.error(f"!ERROR! {log_data}")  # Запись в лог как ERROR
    elif log_type == "debug":
        logging.debug(f"?DEBUG? {log_data}")  # Запись в лог как DEBUG
    else:
        # Если тип лога неизвестен, используем info - как значение по умолчанию
        logging.debug(f"info {log_data}")