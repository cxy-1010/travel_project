"""货币转换与价格比较工具"""

CURRENCY_RATES = {
    'CNY': 1.0,
    'USD': 0.14,
    'EUR': 0.13,
}

CURRENCY_SYMBOLS = {
    'CNY': '¥',
    'USD': '$',
    'EUR': '€',
}

CURRENCY_NAMES = {
    'CNY': '人民币',
    'USD': '美元',
    'EUR': '欧元',
}

# 数据库存储价格为人民币基准
BASE_CURRENCY = 'CNY'


def get_user_currency(request):
    """获取当前用户选择的货币"""
    if request.user.is_authenticated:
        try:
            return request.user.profile.preferred_currency
        except Exception:
            pass
    return request.session.get('currency', 'CNY')


def convert_price(amount, currency):
    """将人民币价格转换为目标货币"""
    rate = CURRENCY_RATES.get(currency, 1.0)
    return round(float(amount) * rate, 2)


def format_price(amount, currency):
    """格式化价格显示"""
    converted = convert_price(amount, currency)
    symbol = CURRENCY_SYMBOLS.get(currency, '¥')
    if currency == 'CNY':
        return f'{symbol}{converted:,.0f}'
    return f'{symbol}{converted:,.2f}'


def get_best_deal(items, price_field='price'):
    """从列表中找出最低价项，用于推荐标签"""
    if not items:
        return None
    return min(items, key=lambda x: float(getattr(x, price_field, 0) or 0))


def get_best_value(items, price_field='price', rating_field='rating'):
    """综合价格和评分推荐最佳性价比"""
    if not items:
        return None

    def score(item):
        price = float(getattr(item, price_field, 0) or 1)
        rating = float(getattr(item, rating_field, 0) or 0)
        return rating / price

    return max(items, key=score)
