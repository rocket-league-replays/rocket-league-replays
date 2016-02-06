import django_filters
from django.contrib.auth.models import User

from .models import Replay, ReplayPack


class ReplayFilter(django_filters.FilterSet):

    player_name = django_filters.filters.CharFilter(
        name='player__player_name',
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

    region = django_filters.filters.ChoiceFilter(
        choices=(
            (None, 'Any'),
            ('EU', 'EU'),
            ('USE', 'US East'),
            ('USW', 'US West'),
            ('OCE', 'Oceania'),
            ('SAM', 'South America'),
        ),
        name='server_name',
        lookup_type='startswith',
    )

    order_by_field = 'order'

    class Meta:
        model = Replay
        fields = ['user', 'map', 'team_sizes', 'season']
        strict = False


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
