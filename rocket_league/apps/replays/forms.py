from django import forms
from django.utils.safestring import mark_safe

from .models import Replay
from ...utils.replay_parser import ReplayParser

import django_filters


class ReplayUploadForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ReplayUploadForm, self).clean()

        # Process the file.
        parser = ReplayParser()
        response = parser.get_id(None, cleaned_data['file'].read(), check=True)

        if isinstance(response, Replay):
            raise forms.ValidationError(mark_safe("This replay has already been uploaded, <a href='{}'>you can view it here</a>.".format(
                response.get_absolute_url()
            )))

    class Meta:
        model = Replay
        fields = ['file']


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
