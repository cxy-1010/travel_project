from django import template
from travel_app.utils import format_price, convert_price

register = template.Library()


@register.filter
def currency_price(amount, currency):
    """模板过滤器：将人民币价格转换为指定货币显示"""
    if amount is None:
        return ''
    return format_price(amount, currency)


@register.filter
def currency_convert(amount, currency):
    """返回转换后的数值"""
    if amount is None:
        return 0
    return convert_price(amount, currency)
