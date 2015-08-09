from django.contrib.auth.models import User

from .models import Replay, ReplayPack

import django_filters


class ReplayFilter(django_filters.FilterSet):

    player_name = django_filters.filters.CharFilter(
        name='player__player_name',
        lookup_type='icontains',
    )

    server_name = django_filters.filters.CharFilter(
        lookup_type='icontains',
    )

    team_sizes = django_filters.filters.ChoiceFilter(
        choices=(
            (None, 'Any'),
            (1, '1v1'),
            (2, '2v2'),
            (3, '3v3'),
            (4, '4v4'),
        )
    )

    match_type = django_filters.filters.ChoiceFilter(
        choices=(
            (None, 'Any'),
            ('Online', 'Online'),
            ('Offline', 'Offline'),
        )
    )

    class Meta:
        model = Replay
        fields = ['map', 'server_name', 'team_sizes', 'match_type']


class ReplayPackFilter(django_filters.FilterSet):

    title = django_filters.filters.CharFilter(
        lookup_type='icontains',
    )

    user = django_filters.filters.ModelChoiceFilter(
        queryset=User.objects.exclude(replay__isnull=True)
    )

    class Meta:
        model = ReplayPack
        fields = ['title', 'user']
