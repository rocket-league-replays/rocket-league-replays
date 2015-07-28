from django import forms
from django.utils.safestring import mark_safe

from .models import Replay
from ...utils.replay_parser import ReplayParser

import django_filters

import struct


class ReplayUploadForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ReplayUploadForm, self).clean()

        if cleaned_data.get('file'):
            # Process the file.
            parser = ReplayParser()

            try:
                replay_data = parser.parse(cleaned_data['file'])

                # Check if this replay has already been uploaded.
                try:
                    replay = Replay.objects.get(
                        replay_id=replay_data['Id']
                    )

                    raise forms.ValidationError(mark_safe("This replay has already been uploaded, <a href='{}'>you can view it here</a>.".format(
                        replay.get_absolute_url()
                    )))
                except Replay.DoesNotExist:
                    # This is a good thing.
                    pass
            except struct.error:
                raise forms.ValidationError("The file you selected does not seem to be a valid replay file.")

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
