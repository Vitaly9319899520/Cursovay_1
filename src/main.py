import logging
import os
import re
import typing

import pandas as pd

from config import DATA_DIR, LOGS_DIR
from src.reports import spending_by_category
from src.services import profitable_cashback
from src.utils import read_exsel
from src.views import web_main

log_file_path = os.path.join(LOGS_DIR, "utils.log")
file_logger = logging.getLogger("utils")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s – %(funcName)s – %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.DEBUG)


@typing.no_type_check
def main():
    """Основная функция, которая формирует логику программы и связывает функциональности между собой"""

    operations_path = os.path.join(DATA_DIR, "operations.xlsx")
    transactions_ex = read_exsel(operations_path)
    transactions = pd.DataFrame(transactions_ex)
    date_pattern = r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$"
    date_pattern_rep = r"^\d{2}\.\d{2}\.\d{4}$"
    data = read_exsel(operations_path)
    data["Дата платежа"] = pd.to_datetime(data["Дата платежа"], format="%d.%m.%Y")
    min_year = data["Дата платежа"].dt.year.min()
    max_year = data["Дата платежа"].dt.year.max()

    date_user = "01-01-2021 12:00:00"
    year_user = "2019"
    month_user = "10"
    category_user = "Супермаркеты"
    date_report = "01.10.2021"

    if re.match(date_pattern, date_user) is False:
        print("Ошибка: введенная дата имеет неверный формат. Попробуйте снова.")
    else:
        result_info = web_main(date_user)

    if year_user.isdigit() and month_user.isdigit():
        year_user = int(year_user)
        month_user = int(month_user)
        if year_user < min_year or year_user > max_year or month_user < 1 or month_user > 12:
            file_logger.error(
                "Ошибка: для анализа введен год, которого нет в файле с транзакциями, "
                "либо месяц должен быть от 1 до 12."
            )
            print(f"Год должен быть в диапазоне от {min_year} до {max_year}.Месяц должен быть от 1 до 12.")
        else:
            result_cashback = profitable_cashback(data, year_user, month_user)
    else:
        print("Год и месяц должны состоять из цифр")

    if re.match(date_pattern_rep, date_report):
        result_report = spending_by_category(transactions, category_user, date_report)
        json_result = result_report.to_json(orient="records")
    else:
        print("Ошибка: введенная дата должна иметь формат %d.%m.%Y.")

    return (
        f"Статистика по дате: {result_info} \n,"
        f"Статистика по категориям, где выгодный кэшбек: {result_cashback}\n,"
        f"Траты по заданной категории за последние 3 месяца с указанной даты: {json_result}"
    )


print(main())
