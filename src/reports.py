import datetime
import logging
import os
import re
import typing
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from config import LOGS_DIR

log_file_path = os.path.join(LOGS_DIR, "reports.log")
file_logger = logging.getLogger("reports")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s – %(funcName)s – %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.DEBUG)


@typing.no_type_check
def save_report_function(filename: str = "standart_report.xlsx"):
    """Функция-декоратор, которая записывает ответ, сгенерированный функцией-отчетом, \
    в отдельный файл с расширением xlsx"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result.to_excel(filename, index=False)
            file_logger.info(f"Отчет успешно записан в файл {filename}")
            print(f"Отчет сохранен в файл: {filename}")
            return result

        return wrapper

    return decorator


@save_report_function("result_function.xlsx")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция, которая возвращает траты по заданной категории за последние 3 месяца"""

    date_pattern_rep = r"^\d{2}\.\d{2}\.\d{4}$"
    file_logger.info("Начало работы функции")
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")
    if date is None:
        date = datetime.datetime.now().strftime("%d.%m.%Y")

    if re.match(date_pattern_rep, date):
        date_end = datetime.datetime.strptime(date, "%d.%m.%Y")
        date_start = date_end - relativedelta(months=3)
        filtered_df = transactions[
            (transactions["Категория"] == category)
            & (transactions["Дата платежа"] >= date_start)
            & (transactions["Дата платежа"] <= date_end)
        ]

        if filtered_df.empty:
            file_logger.error(f"Данные не найдены, либо расходов по категории {category} в заданный период не было.")
            raise ValueError(f"Не найдены расходы по категории {category} за указанный период")
        else:
            total_sum = filtered_df["Сумма операции с округлением"].sum()

            result = pd.DataFrame(
                {
                    "category": [category],
                    "total_sum": [total_sum],
                    "date_start": [date_start.strftime("%Y-%m-%d")],
                    "date_end": [date_end.strftime("%Y-%m-%d")],
                }
            )
            file_logger.info("Успешное окончание работы функции")
            return result
    else:
        raise ValueError('Дата должна быть формата "%d.%m.%Y"')
