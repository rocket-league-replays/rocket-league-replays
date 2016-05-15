from django import forms

from .models import Replay, ReplayPack


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
                        initial=user_players[x].player_name if len(user_players) >= x + 1 else '',
                        required=False,
                    )

    class Meta:
        model = Replay
        fields = ['title', 'privacy']


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
