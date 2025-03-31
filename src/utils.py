import datetime
import json
import logging
import os
import typing

import pandas as pd
import requests
from dotenv import load_dotenv

from config import LOGS_DIR

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_ALPHA = os.getenv("API_KEY_ALPHA")

log_file_path = os.path.join(LOGS_DIR, "utils.log")
file_logger = logging.getLogger("utils")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s – %(funcName)s – %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.DEBUG)


def hello_date() -> str:
    """Функция, которая в зависимости от текущего времени возвращает пользователю разные приветствия"""

    day_now = datetime.datetime.now()
    time_now = day_now.hour
    if time_now >= 0 and time_now < 6:
        greeting = "Доброй ночи"
        return greeting
    elif time_now >= 6 and time_now < 12:
        greeting = "Доброе утро"
        return greeting
    elif time_now >= 12 and time_now < 18:
        greeting = "Добрый день"
        return greeting
    else:
        greeting = "Добрый вечер"
        return greeting


def read_exsel(operations_path: str) -> pd.DataFrame:
    """Функция чтения файла Exsel с банковскими транзакицями"""

    required_columns = [
        "Дата операции",
        "Номер карты",
        "Сумма операции",
        "Сумма платежа",
        "Кэшбэк",
        "Сумма операции с округлением",
    ]
    if os.path.exists(operations_path):
        excel_df = pd.read_excel(operations_path)
        if excel_df.empty:
            raise ValueError("Анализируемый файл пустой")
        else:
            for column in required_columns:
                if column not in excel_df.columns:
                    raise ValueError(f"Отсутствует необходимый столбец: {column}")
            return excel_df
    else:
        raise ValueError("Файл с транзакциями не найден")


def read_json(operations_path_json: str) -> typing.Any:
    """Функция чтения файла JSON с пользовательскими настройками,
    где хранятся данные о валютах и акциях, которые будут использоваться
    для отображения на web-страницах"""

    if os.path.exists(operations_path_json):
        with open(operations_path_json, "r", encoding="UTF-8") as f:
            try:
                data = json.load(f)
                return data
            except ValueError as e:
                return f"Ошибка чтения файла: {e}"
    else:
        raise ValueError("Файл с настройками не найден")


def kart_user_info(user_date: str, operations_path: str) -> typing.Any:
    """Функция, которая возвращает информацию из файла транзакций по карте:
    последние 4 цифры номера карты, общая сумма расходов и кэшбек"""

    excel_df = read_exsel(operations_path)
    excel_df["Дата операции"] = pd.to_datetime(excel_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    start_date = user_date
    end_date = datetime.datetime.now()
    filtered_df = excel_df[(excel_df["Дата операции"] >= start_date) & (excel_df["Дата операции"] <= end_date)]
    group_df = (
        filtered_df.groupby("Номер карты")
        .agg(total_spent=("Сумма операции с округлением", "sum"), cashback=("Кэшбэк", "sum"))
        .reset_index()
    )
    group_df = group_df.rename(columns={"Номер карты": "last_digits"})
    file_logger.info("Все данные по карте, общая сумма расходов и кэшбек успешно рассчитаны.")
    return group_df.to_dict(orient="records")


def top_transactions(user_date: str, operations_path: str) -> typing.Any:
    """Функция, которая выдает топ-5 транзакций по сумме платежа"""

    excel_df = read_exsel(operations_path)
    excel_df["Дата операции"] = pd.to_datetime(excel_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    start_date = user_date
    end_date = datetime.datetime.now()
    filtered_date = excel_df[(excel_df["Дата операции"] >= start_date) & (excel_df["Дата операции"] <= end_date)]
    filtered_sum = filtered_date.sort_values(by="Сумма операции с округлением", ascending=False).head(5)
    filtered_sum["Дата операции"] = filtered_sum["Дата операции"].dt.strftime("%d.%m.%Y")
    filtered_sum = filtered_sum.rename(
        columns={
            "Дата операции": "date",
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description",
        }
    )
    filtered_sum = filtered_sum[["date", "amount", "category", "description"]]
    file_logger.info("Топ-5 транзакций по сумме платежа успешно отобраны")
    return filtered_sum.to_dict(orient="records")


def exchange_rate(operations_path_json: str) -> typing.Any:
    """Функция, которая возвращает курс валют, которые указаны
    в файле  user_settings, к рублю на текущую дату"""

    user_settings = read_json(operations_path_json)
    currency_base = user_settings.get("user_currencies", [])
    currency_rub = "RUB"
    headers = {"apikey": API_KEY}
    exchange_rates = {}
    file_logger.info("Начало выполнения функции")
    for currency in currency_base:
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={currency_rub}&base={currency}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result_answer = response.json()
                if "rates" in result_answer and currency_rub in result_answer["rates"]:
                    exchange_rates[currency] = float(result_answer["rates"][currency_rub])
                else:
                    file_logger.warning(f"Курс для {currency} не найден.")
                    print(f"Курс для {currency} не найден.")
            else:
                file_logger.warning(f"Ошибка конвертации валюты ({currency}): {response.status_code}")
                print(f"Ошибка конвертации валюты ({currency}): {response.status_code}")
        except requests.exceptions.RequestException as e:
            file_logger.error(f"Ошибка конвертации {e}")
            print(f"Ошибка конвертации: {e}")

        result = [{"currency": key, "rate": value} for key, value in exchange_rates.items()]
    file_logger.info("Функция успешно выполнена")
    return result


def stock_prices(operations_path_json: str) -> typing.Any:
    """Функция, которая возвращает стоимость акций из S&P500 на текущую дату"""

    user_settings = read_json(operations_path_json)
    currency_stocks = user_settings.get("user_stocks", [])
    results = []
    file_logger.info("Начало выполнения функции")
    for currency in currency_stocks:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={currency}&apikey={API_KEY_ALPHA}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                result_answer = response.json()
                if "Time Series (Daily)" in result_answer:
                    latest_date = next(iter(result_answer["Time Series (Daily)"]))
                    latest_price = float(result_answer["Time Series (Daily)"][latest_date]["4. close"])
                    results.append({"stock": currency, "price": latest_price})
                else:
                    file_logger.warning(f"Нет данных о цене для {currency}.")
                    print(f"Нет данных о цене для {currency}.")
            else:
                file_logger.warning(f"Цена для {currency} не найдена. Cтатус: {response.status_code}.")
                print(f"Цена для {currency} не найдена. Cтатус: {response.status_code}.")
        except requests.exceptions.RequestException as e:
            file_logger.error(f"Ошибка запроса: {e}")
            print(f"Ошибка запроса: {e}")
    file_logger.info("Функция успешно выполнена")
    return results
