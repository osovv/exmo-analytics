import locale
import os
from decimal import Decimal

from exmoapi import ExmoApi
from utils import get_usd_course

# Публичный и приватный ключи EXMO API
PUBLIC_KEY = os.getenv('EXMO_PUBLIC_KEY')
SECRET_KEY = os.getenv('EXMO_SECRET_KEY')

api = ExmoApi(PUBLIC_KEY, SECRET_KEY)
usd_course = get_usd_course()
print(f"Текущий курс доллара (ЦБ РФ): {usd_course} руб.")


def get_balance_in_rub() -> int:
    """
    Возвращает текущую стоимость портфеля в рублях без учёта
    лежащих на аккаунте RUB, но с учётом лежащих на аккаунте USD
    """
    balances = api.get_all_balances()
    courses = api.get_courses()

    balance_in_usd = Decimal('0')
    for coin_name, amount in balances.items():
        if coin_name == 'RUB':
            continue
        if coin_name == 'USD':
            balance_in_usd += Decimal(amount)
            continue
        value_usd_course = courses.get(f'{coin_name}_USD', 0)
        balance_in_usd += Decimal(str(Decimal(amount) * Decimal(value_usd_course)))

    return int(balance_in_usd * usd_course)


def get_deposit_in_rub() -> int:
    """
    Возвращает сумму всех пополнений в рублях
    """
    wallet_operations = api.get_all_operations()
    deposit_rub = Decimal(0)
    for operation in wallet_operations['items']:
        if operation['type'] == 'deposit' and operation['provider'] != 'CashBack':
            if operation['currency'] == 'RUB':
                deposit_rub += Decimal(operation['amount'])
    return int(deposit_rub)


balance_in_rub = get_balance_in_rub()
deposit_in_rub = get_deposit_in_rub()
profit_in_rub = balance_in_rub - deposit_in_rub
profit_in_percent = round(100 * round(profit_in_rub / deposit_in_rub, 4),2)

print(f"Пополнения: {deposit_in_rub:2} руб.\n"
      f"Текущая стоимость портфеля: {balance_in_rub:2} руб.\n"
      f"Прибыль: {profit_in_rub:2} руб. ({profit_in_percent:2} %)")
