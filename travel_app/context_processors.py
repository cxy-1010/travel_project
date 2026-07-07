from .utils import CURRENCY_RATES, CURRENCY_SYMBOLS, CURRENCY_NAMES, get_user_currency


def currency_context(request):
    currency = get_user_currency(request)
    return {
        'current_currency': currency,
        'currency_symbol': CURRENCY_SYMBOLS.get(currency, '¥'),
        'currency_rates': CURRENCY_RATES,
        'currency_choices': CURRENCY_NAMES,
    }
