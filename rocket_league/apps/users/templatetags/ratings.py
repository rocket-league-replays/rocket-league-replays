from django import template
from django.conf import settings

from ...replays.models import PLATFORM_STEAM, get_default_season
from ..models import LeagueRating

register = template.Library()


@register.assignment_tag(takes_context=True)
def latest_ratings(context):
    return LeagueRating.objects.filter(
        platform=PLATFORM_STEAM,
        online_id=context['steam_id'],
    )


@register.assignment_tag
def get_ratings(uid):
    return LeagueRating.objects.filter(
        steamid=uid,
        season_id=get_default_season(),
    )[:50]


@register.simple_tag
def playlist_name(playlist, remove_prefix=False):
    if playlist in settings.HUMAN_PLAYLISTS:
        if remove_prefix:
            return settings.HUMAN_PLAYLISTS[playlist].replace('Ranked ', '')
        return settings.HUMAN_PLAYLISTS[playlist]
    return playlist


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
