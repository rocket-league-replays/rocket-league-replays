from django import template

from ...replays.models import Player
from ..models import Patron

register = template.Library()


@register.filter
def wrap(val, func):
    return eval(func)(val)


@register.filter
def order_by(qs, ordering):
    return qs.order_by(ordering)


@register.assignment_tag
def display_names(steam_info):
    if not steam_info:
        return None

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


@register.filter
def string(val):
    return str(val)


@register.assignment_tag(takes_context=True)
def patreon_pledge_amount(context):
    user = context['user']

    if not user.is_authenticated():
        return 0

    # Does this user have a Patreon email address?
    if not user.profile.patreon_email_address:
        return 0

    # Does a patreon object for this email address exist?
    try:
        obj = Patron.objects.get(
            patron_email=user.profile.patreon_email_address,
        )

        if obj.pledge_declined_since:
            # TODO: Double check this is correct.
            return 0

        return obj.pledge_amount

    except Patron.DoesNotExist:
        return 0


@register.assignment_tag(takes_context=True)
def patreon_pledge_amount_dollars(context):
    return '{0:.2f}'.format(context['patreon'] / 100.0)
