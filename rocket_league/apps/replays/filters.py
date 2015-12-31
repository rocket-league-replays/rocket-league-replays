from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum, ExpressionWrapper


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

    excitement_factor = django_filters.filters.NumberFilter(
        lookup_type='gte',
    )

    total_goals = django_filters.filters.NumberFilter(
        action=lambda qs, value: qs.annotate(
            goals=Sum(F('team_0_score') + F('team_1_score'))
        ).filter(goals=value)
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

    match_length = django_filters.filters.NumberFilter(
        label='Match length (in seconds)',
        action=lambda qs, value: qs.annotate(
            seconds=ExpressionWrapper(
                F('num_frames') / F('record_fps'),
                output_field=models.IntegerField()
            )
        ).filter(
            seconds__gte=value,
        )
    )

    order_by_field = 'order'

    class Meta:
        model = Replay
        fields = ['map', 'server_name', 'team_sizes', 'excitement_factor']
        strict = False
        # order_by = ['-average_rating', '-excitement_factor']

        # order_by = [
        #     ('-average_rating', 'Average rating'),
        #     ('average_rating', 'Average rating'),
        #     ('-excitement_factor', 'Excitement factor'),
        #     ('excitement_factor', 'Excitement factor'),
        #     ('-timestamp', 'Date'),
        #     ('timestamp', 'Date'),
        #     ('-num_frames', 'Length'),
        #     ('num_frames', 'Length'),
        # ]


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
