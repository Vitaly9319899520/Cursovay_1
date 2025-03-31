import json

import pytest

from src.services import profitable_cashback


@pytest.mark.parametrize(
    "year, month, expected",
    [(2023, 1, {"Продукты": 4.5, "Развлечения": 2.5}), (2023, 2, {"Продукты": 3, "Туризм": 8.5, "Развлечения": 3.5})],
)
def test_profitable_cashback(sample_data, year, month, expected):
    """Тестирует функцию profitable_cashback с заданными годом и месяцем."""
    result = profitable_cashback(sample_data, year, month)
    assert json.loads(result) == expected


def test_profitable_cashback_empty_result(sample_data):
    """Тестирует сценарий с пустым результатом."""
    with pytest.raises(ValueError) as excinfo:
        profitable_cashback(sample_data, 2023, 3)
    assert "Проверьте правильность переданных данных. Словарь не создан." in str(excinfo.value)


def test_profitable_cashback_correct_structure(sample_data):
    """Тестирует правильную структуру результата для корректного ввода."""
    result = profitable_cashback(sample_data, 2023, 1)
    result_dict = json.loads(result)
    assert isinstance(result_dict, dict)
    assert "Продукты" in result_dict
    assert "Развлечения" in result_dict


def test_profitable_cashback_month(sample_data):
    """Тестирует сценарий с ошибочным месяцем."""
    with pytest.raises(ValueError) as excinfo:
        profitable_cashback(sample_data, 2023, 15)
    assert "Месяц должен быть в диапазоне от 1 до 12" in str(excinfo.value)


def test_profitable_cashback_year(sample_data):
    """Тестирует сценарий с ошибочным годом."""

    with pytest.raises(ValueError) as excinfo:
        profitable_cashback(sample_data, 2025, 10)
    assert "Год должен быть в диапазоне от 2023 до 2023." in str(excinfo.value)
