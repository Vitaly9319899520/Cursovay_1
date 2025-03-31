import json
import logging
import os
import re
import typing

from config import DATA_DIR, LOGS_DIR, ROOT_DIR
from src.utils import exchange_rate, hello_date, kart_user_info, stock_prices, top_transactions

operations_path = os.path.join(DATA_DIR, "operations.xlsx")
operations_path_json = os.path.join(ROOT_DIR, "user_settings.json")

log_file_path = os.path.join(LOGS_DIR, "views.log")
file_logger = logging.getLogger("views")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.DEBUG)


def web_main(date_time: str) -> typing.Any:
    """Главная функция, которая принимает на вход строку с датой и временем в формате
    DD-MM-YYYY HH:MM:SS и возвращающую JSON-ответ со следующими данными:
    - приветствие, в зависимости от времени текущего суток
    - статистику по каждой карте в выбранный промежуток времени
    - топ-5 транзакций по сумме платежа
    - курс валют
    - Стоимость акций из S&P500"""

    date_pattern = r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$"
    if re.match(date_pattern, date_time):
        result_total = {}
        result_total["greeting"] = hello_date()
        result_total["cards"] = kart_user_info(date_time, operations_path)
        result_total["top_transactions"] = top_transactions(date_time, operations_path)
        result_total["currency_rates"] = exchange_rate(operations_path_json)
        result_total["stock_prices"] = stock_prices(operations_path_json)

        json_result = json.dumps(result_total, ensure_ascii=False)
        if json_result != {}:
            file_logger.info("JSON-ответ успешно сформирован")
            return json_result
        else:
            file_logger.error("JSON-ответ не сформирован")
            raise ValueError("Проверьте правильность входных данных")
    else:
        file_logger.error("Введите дату в формате DD-MM-YYYY HH:MM:SS")
        raise ValueError("Введите дату в формате DD-MM-YYYY HH:MM:SS")
