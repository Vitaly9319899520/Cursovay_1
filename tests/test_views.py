import json
import unittest
from unittest.mock import patch

from src.views import web_main


@patch("src.views.hello_date")
@patch("src.views.kart_user_info")
@patch("src.views.top_transactions")
@patch("src.views.exchange_rate")
@patch("src.views.stock_prices")
def test_valid_input(
    mock_stock_prices, mock_exchange_rate, mock_top_transactions, mock_kart_user_info, mock_hello_date
):
    # Настройка возвратов для моков
    mock_hello_date.return_value = "Доброе утро"
    mock_kart_user_info.return_value = {"card_1": "info_1", "card_2": "info_2"}
    mock_top_transactions.return_value = [{"id": 1, "amount": 150}, {"id": 2, "amount": 100}]
    mock_exchange_rate.return_value = {"USD": 74.5, "EUR": 88.0}
    mock_stock_prices.return_value = {"AAPL": 150.0, "GOOGL": 2800.0}

    test_date_time = "15-10-2022 08:00:00"
    expected_output = {
        "greeting": "Доброе утро",
        "cards": {"card_1": "info_1", "card_2": "info_2"},
        "top_transactions": [{"id": 1, "amount": 150}, {"id": 2, "amount": 100}],
        "currency_rates": {"USD": 74.5, "EUR": 88.0},
        "stock_prices": {"AAPL": 150.0, "GOOGL": 2800.0},
    }

    result = web_main(test_date_time)

    assert json.loads(result) == expected_output


def test_invalid_date_format():
    with unittest.TestCase().assertRaises(ValueError) as context:
        web_main("2022-10-15 08:00:00")

    assert str(context.exception) == "Введите дату в формате DD-MM-YYYY HH:MM:SS"
