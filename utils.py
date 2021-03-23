from datetime import datetime
from decimal import Decimal

from pycbrf import ExchangeRates
from pytz import timezone


def localize(d: datetime) -> datetime:
    return timezone('Europe/Moscow').localize(d)


def get_now() -> datetime:
    return localize(datetime.now())


def get_formatted_now(format_: str = "%Y-%m-%d") -> str:
    return get_now().strftime(format_)


def get_usd_course() -> Decimal:
    """ Возвращает текущий курс доллара от ЦБ РФ."""
    rates = ExchangeRates(get_formatted_now())
    return Decimal(rates['USD'].value)
