import datetime

import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta

from src.reports import spending_by_category


def test_spending_by_category_valid(sample_transactions):
    """Тест для корректного выбора расходов по категории за последний период."""
    result = spending_by_category(sample_transactions, "еда", "10.03.2023")
    assert result.shape[0] == 1
    assert result["total_sum"].values[0] == 500  # 100 + 150 + 250
    assert result["date_start"].values[0] == (
        datetime.datetime.strptime("10.03.2023", "%d.%m.%Y") - relativedelta(months=3)
    ).strftime("%Y-%m-%d")
    assert result["date_end"].values[0] == "2023-03-10"


def test_spending_by_category_no_data(sample_transactions):
    """Тест для случая, когда данных по категории нет."""
    with pytest.raises(ValueError, match="Не найдены расходы по категории"):
        spending_by_category(sample_transactions, "развлечения", "01.01.2023")


def test_spending_by_category_invalid_date_format(sample_transactions):
    """Тест для неправильного формата даты."""
    with pytest.raises(ValueError, match='Дата должна быть формата "%d.%m.%Y"'):
        spending_by_category(sample_transactions, "еда", "2023-03-10")


def test_spending_by_category_no_transactions(sample_transactions):
    """Тестирование функции, когда нет транзакций."""
    empty_df = pd.DataFrame(columns=["Категория", "Дата платежа", "Сумма операции с округлением"])
    with pytest.raises(ValueError, match="Не найдены расходы по категории"):
        spending_by_category(empty_df, "еда", "10.03.2023")
