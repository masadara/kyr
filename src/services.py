from datetime import datetime
import pandas as pd
import os
import re


def xlsx_transactions(path: str) -> list[dict]:
    """Функция вывода транзакций с XLSX файла"""
    df = pd.read_excel(path)
    # print(df.shape)
    operations_full = df.to_dict(orient="records")
    result = []
    for item in operations_full:
        result.append(item)
    return result


def cashback(data: list[dict], year: int, month: int) -> dict:
    """Функция анализа кешбэка"""
    res = {}
    for item in data:
        date_transaction = datetime.strptime(
            item.get("Дата операции"), "%d.%m.%Y %H:%M:%S"
        )
        if year == date_transaction.year and month == date_transaction.month:
            categoty = item.get("Категория")
            cashback_amount = round(abs(item.get("Сумма платежа") / 100), 2)
            cashback_amount = round(cashback_amount, 2)
            if categoty not in res:
                res[categoty] = 0
            res[categoty] += round(cashback_amount, 2)
    return res


def search(query: str, data: list[dict]) -> list[dict]:
    """Функция простого поиска"""
    result = []
    for item in data:
        if re.search(query, str(item.get("Описание"))) or re.findall(
            query, str(item.get("Категория"))
        ):
            result.append(item)
    return result


def search_mobile(data: list[dict]) -> list[dict]:
    """Функция поиска номера телефона в описании"""
    pattern = re.compile(r"((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}")
    result = []
    for item in data:
        if re.search(pattern, str(item.get("Описание"))):
            result.append(item)
    return result


path_to_xlsx = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
# print(cashback(xlsx_transactions(path_to_xlsx), 2021, 12))
# print(search('Олеся', xlsx_transactions(path_to_xlsx)))
print(search_mobile(xlsx_transactions(path_to_xlsx)))
