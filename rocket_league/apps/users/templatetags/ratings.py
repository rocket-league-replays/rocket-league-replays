from django import template
from django.conf import settings

from ...replays.models import get_default_season
from ..models import Profile, LeagueRating


register = template.Library()


@register.assignment_tag(takes_context=True)
def league_data(context):
    # Does this user have their Steam account connected?
    user = context.request.user

    if not user.is_authenticated():
        return

    try:
        assert user.profile
    except Exception as e:
        print(e.__class__.__name__)

        if e.__class__.__name__ == 'RelatedObjectDoesNotExist':
            Profile.objects.create(
                user=user
            )

    return user.profile.latest_ratings()


@register.assignment_tag(takes_context=True)
def latest_ratings(context):
    ratings = LeagueRating.objects.filter(
        steamid=context['steam_id'],
        season_id=get_default_season(),
    )[:1]

    if ratings.count() > 0:
        return {
            settings.PLAYLISTS['RankedDuels']: ratings[0].duels,
            '{}_division'.format(settings.PLAYLISTS['RankedDuels']): ratings[0].duels_division,
            settings.PLAYLISTS['RankedDoubles']: ratings[0].doubles,
            '{}_division'.format(settings.PLAYLISTS['RankedDoubles']): ratings[0].doubles_division,
            settings.PLAYLISTS['RankedSoloStandard']: ratings[0].solo_standard,
            '{}_division'.format(settings.PLAYLISTS['RankedSoloStandard']): ratings[0].solo_standard_division,
            settings.PLAYLISTS['RankedStandard']: ratings[0].standard,
            '{}_division'.format(settings.PLAYLISTS['RankedStandard']): ratings[0].standard_division,
        }


@register.assignment_tag
def get_ratings(uid):
    return LeagueRating.objects.filter(
        steamid=uid,
        season_id=get_default_season(),
    )[:50]


@register.simple_tag
def league_name(tier):
    if tier in settings.TIERS:
        return settings.TIERS[tier]
    return tier


@register.simple_tag
def division_name(division):
    if division in settings.DIVISIONS:
        return settings.DIVISIONS[division]
    return division


@register.filter
def league_image(tier):
    return tier in settings.TIERS
