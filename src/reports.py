import pandas as pd
import os
from datetime import datetime, timedelta
import functools


def report_to_file(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        filename = "report_{}.csv".format(func.__name__)
        with open(filename, "w") as file:
            result.to_csv(file)
        return result

    return wrapper


def report_to_custom_file(filename):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(filename, "w") as file:
                result.to_csv(file)
            return result

        return wrapper

    return decorator


def xlsx_transactions(path: str) -> pd.DataFrame:
    """Функция вывода транзакций с XLSX файла"""
    df = pd.read_excel(path)
    # print(df.shape)
    operations_full = df.to_dict(orient="records")
    result = []
    for item in operations_full:
        result.append(item)
    result = pd.DataFrame(result)
    return result


@report_to_custom_file("report_name.csv")
@report_to_file
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: str = "31.12.2021"
) -> pd.DataFrame:
    '''Функция поиска транзакций по категории за 3 месяца'''
    result = []
    date_cur = datetime.strptime(date, "%d.%m.%Y")
    for item in transactions.to_dict("records"):
        if (
            item.get("Категория") == category
            and datetime.strptime(item.get("Дата операции"), "%d.%m.%Y %H:%M:%S")
            <= date_cur
            and datetime.strptime(item.get("Дата операции"), "%d.%m.%Y %H:%M:%S")
            >= date_cur - timedelta(days=90)
        ):
            result.append(item)
    return pd.DataFrame(result)


path_to_xlsx = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
# print(xlsx_transactions(path_to_xlsx))
# print(spending_by_category(xlsx_transactions(path_to_xlsx), 'Такси'))
spending_by_category(xlsx_transactions(path_to_xlsx), "Такси")
