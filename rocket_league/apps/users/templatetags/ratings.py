from django import template
from django.conf import settings

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
        print e.__class__.__name__

        if e.__class__.__name__ == 'RelatedObjectDoesNotExist':
            Profile.objects.create(
                user=user
            )

    return user.profile.latest_ratings()


@register.assignment_tag(takes_context=True)
def latest_ratings(context):
    ratings = LeagueRating.objects.filter(
        steamid=context['steam_id'],
    )[:1]

    if ratings:
        return {
            settings.PLAYLISTS['RankedDuels']: ratings[0].duels,
            settings.PLAYLISTS['RankedDoubles']: ratings[0].doubles,
            settings.PLAYLISTS['RankedSoloStandard']: ratings[0].solo_standard,
            settings.PLAYLISTS['RankedStandard']: ratings[0].standard,
        }


@register.assignment_tag
def get_ratings(uid):
    print 'getting ratings for', uid
    return LeagueRating.objects.filter(
        steamid=uid,
    )
