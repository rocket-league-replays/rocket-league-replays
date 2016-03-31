from django import template
from django.utils.timezone import now
from social.apps.django_app.default.models import UserSocialAuth

from ...replays.models import Player
from ..models import Patron, PatronTrial

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
        platform__in=['OnlinePlatform_Steam', '1'],
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
def patreon_pledge_amount(context, user=None, steam_id=None):
    # Check if we need to take the user from the context data.
    if not user and not steam_id:
        user = context['user']

        if not user.is_authenticated():
            return 0

    if not user and steam_id:
        # See if we can get a user object from this Steam ID.
        try:
            obj = UserSocialAuth.objects.get(
                provider='steam',
                uid=steam_id,
            )

            user = obj.user

        except UserSocialAuth.DoesNotExist:
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
        # Does an active trial for this user exist?
        try:
            PatronTrial.objects.get(
                user=user,
                expiry_date__gte=now().date,
            )

            return 99999
        except PatronTrial.DoesNotExist:
            return 0

        return 0


@register.assignment_tag(takes_context=True)
def patreon_pledge_amount_dollars(context):
    return '{0:.2f}'.format(context['patreon'] / 100.0)
