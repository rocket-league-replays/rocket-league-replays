from django import template
from django.conf import settings

from ...replays.models import PLATFORM_STEAM
from ..models import LeagueRating

register = template.Library()


@register.assignment_tag(takes_context=True)
def latest_ratings(context):
    ratings = LeagueRating.objects.filter_or_request(
        platform=context['platform'],
        online_id=context['player_id'],
    )

    if ratings:
        return ratings

    # Add some default values.
    return [
        {
            'playlist': playlist,
            'tier': 0,
        }
        for playlist in settings.RANKED_PLAYLISTS
    ]


@register.simple_tag
def playlist_name(playlist, remove_prefix=False):
    if playlist in settings.HUMAN_PLAYLISTS:
        if remove_prefix:
            return settings.HUMAN_PLAYLISTS[playlist].replace('Ranked ', '')
        return settings.HUMAN_PLAYLISTS[playlist]
    return 'Unknown'


@register.simple_tag
def tier_name(tier):
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
