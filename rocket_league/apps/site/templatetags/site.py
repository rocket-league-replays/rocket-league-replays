from django import template

register = template.Library()


@register.filter
def wrap(val, func):
    return eval(func)(val)
