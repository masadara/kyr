import json
from datetime import datetime
import pandas as pd
import os
from operator import itemgetter
import requests
from dotenv import load_dotenv

main_res = {
    "greeting": "",
    "cards": [],
    "top_transactions": [],
    "currency_rates": [],
    "stock_prices": []
}

cards_mask = {
    "last_digits": "",
    "total_spent": 0.00,
    "cashback": 0.00
}

top_transactions_mask = {
    "date": "",
    "amount": 0.00,
    "category": "",
    "description": ""
}

currency_rates_mask = {
    "currency": "",
    "rate": 0.00
}

stock_prices_mask = {
    "stock": "",
    "price": 0.00
}

def main_func(date_cur: str) -> list[dict]:
    date = datetime.strptime(date_cur, '%Y-%m-%d %H:%M:%S')
    if date.hour < 6 or date.hour >= 21:
        print('Доброй ночи')
        hello = 'Доброй ночи'
    elif date.hour <= 11:
        print('Доброе утро')
        hello = 'Доброе утро'
    else:
        print('Добрый день')
        hello = 'Добрый день'
    path_to_xlsx = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
    transactions_full = xlsx_transactions(path_to_xlsx, date_cur)
    main_res["greeting"] = hello
    cards(transactions_full)
    top_transactions(transactions_full)
    marketstack_api()
    currency_rates()
    return transactions_full


def xlsx_transactions(path: str, date_cur) -> list[dict]:
    """Функция вывода транзакций с XLSX файла"""
    df = pd.read_excel(path)
    # print(df.shape)
    operations_full = df.to_dict(orient="records")
    result = []
    date_cur = datetime.strptime(date_cur, '%Y-%m-%d %H:%M:%S')
    for item in operations_full:
        date = datetime.strptime(item.get('Дата операции'), '%d.%m.%Y %H:%M:%S')
        if date.month == date_cur.month and date.day <= date_cur.day and date.year == date_cur.year:
            result.append(item)
    return result

def cards(operations: list[dict]):
    cards_mask_copy = cards_mask
    cards_uniq = []
    for item in operations:
        cards_uniq.append(item.get('Номер карты')[-4:])
    cards_uniq = list(set(cards_uniq))
    for card in cards_uniq:
        amount = 0
        for item in operations:
            if item.get('Номер карты')[-4:] == card:
                amount += item.get('Сумма операции')
        cards_mask_copy["last_digits"] = card
        cards_mask_copy["total_spent"] = amount
        cards_mask_copy["cashback"] = round(abs(amount / 100), 2)
        main_res["cards"].append(cards_mask_copy.copy())
    print(len(operations))


def top_transactions(operations: list[dict]):
    top_transactions_mask_copy = top_transactions_mask
    sorted_operations = sorted(operations, key=itemgetter("Сумма операции"))
    for item in sorted_operations[:5]:
        top_transactions_mask_copy['date'] = item.get('Дата операции')
        top_transactions_mask_copy['amount'] = abs(item.get('Сумма операции'))
        top_transactions_mask_copy['category'] = item.get('Категория')
        top_transactions_mask_copy['description'] = item.get('Описание')
        main_res["top_transactions"].append(top_transactions_mask_copy.copy())

def marketstack_api():
    stock_prices_mask_copy = stock_prices_mask
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    path_to_json = os.path.join(os.path.dirname(__file__), "..", "user_settings.json")
    with open(path_to_json, encoding="utf8") as json_file:
        user_settings = json.load(json_file)
    for item in user_settings["user_stocks"]:
        url = f"https://api.marketstack.com/v1/eod?access_key={API_KEY}"
        querystring = {"symbols": f"{item}"}
        response = requests.get(url, params=querystring)
        stock_prices_mask_copy["stock"] = item
        stock_prices_mask_copy["price"] = response.json()["data"][0]["open"]
        main_res["stock_prices"].append(stock_prices_mask_copy.copy())


def currency_rates():
    currency_rates_mask_copy = currency_rates_mask
    url = f"https://www.cbr-xml-daily.ru//daily_json.js"
    path_to_json = os.path.join(os.path.dirname(__file__), "..", "user_settings.json")
    with open(path_to_json, encoding="utf8") as json_file:
        user_settings = json.load(json_file)
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to get currency rate")
    data = response.json()
    for items in user_settings["user_currencies"]:
        currency_data = data["Valute"].get(items)
        currency_rates_mask_copy["currency"] = items
        currency_rates_mask_copy["rate"] = currency_data["Value"]
        main_res["currency_rates"].append(currency_rates_mask_copy.copy())


# path_to_xlsx = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
# transactions_full = xlsx_transactions(path_to_xlsx, '02.12.2021 6:44:00')
# print(transactions_full)
print(main_func('2021-12-02 6:44:00'))
print(main_res)