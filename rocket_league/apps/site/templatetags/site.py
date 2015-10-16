from django import template

register = template.Library()


@register.filter
def wrap(val, func):
    return eval(func)(val)


@register.filter
def order_by(qs, ordering):
    return qs.order_by(ordering)
