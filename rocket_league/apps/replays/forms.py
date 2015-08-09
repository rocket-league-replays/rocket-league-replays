from django import forms
from django.utils.safestring import mark_safe

from .models import Replay, ReplayPack
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


class ReplayUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReplayUpdateForm, self).__init__(*args, **kwargs)

        # How many players do we know about in Team 0?
        for team in range(2):
            team_players = kwargs['instance'].player_set.filter(
                team=team,
                user_entered=False,
            ).count()

            if team_players < kwargs['instance'].team_sizes:
                # Fill in with extra fields.
                for x in range(kwargs['instance'].team_sizes - team_players):
                    # Is there a user-entered value for this player already?
                    user_players = kwargs['instance'].player_set.filter(
                        team=team,
                        user_entered=True,
                    )

                    self.fields['team_{}_player_{}'.format(
                        team,
                        x + team_players + 1,
                    )] = forms.CharField(
                        label="{} team, player {}".format(
                            'Blue' if team == 0 else 'Orange',
                            x + team_players + 1,
                        ),
                        initial=user_players[x].player_name if len(user_players) >= x+1 else '',
                        required=False,
                    )

    class Meta:
        model = Replay
        fields = ['title']


class ReplayPackForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ReplayPackForm, self).__init__(*args, **kwargs)

        self.fields['replays'].choices = [
            (replay.pk, str(replay)) for replay in user.replay_set.all()
        ]

    class Meta:
        model = ReplayPack
        fields = ['title', 'replays']
        widgets = {
            'replays': forms.CheckboxSelectMultiple,
        }
