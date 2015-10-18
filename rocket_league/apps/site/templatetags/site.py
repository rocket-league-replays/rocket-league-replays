from django import template

from ...replays.models import Player

register = template.Library()


@register.filter
def wrap(val, func):
    return eval(func)(val)


@register.filter
def order_by(qs, ordering):
    return qs.order_by(ordering)


@register.assignment_tag
def display_names(steam_info):
    names = Player.objects.filter(
        platform='OnlinePlatform_Steam',
        online_id=steam_info['steamid'],
    ).exclude(
        player_name=steam_info.get('personaname', '')
    ).distinct('player_name').values_list(
        'player_name',
        flat=True
    ).order_by()

    if not names:
        return None

    if ',' in ''.join(names):
        return '; '.join(names)
    return ', '.join(names)
