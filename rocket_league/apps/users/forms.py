from django import forms
from django.contrib.auth.models import User

from .models import Profile


class UserSettingsForm(forms.ModelForm):

    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'password_incorrect': "Your current password was entered incorrectly. Please enter it again.",
    }

    old_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput,
        required=False,
    )

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        required=False,
    )

    new_password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput,
        required=False,
    )

    def clean(self):
        """
        Validates that the old_password field is correct.
        """
        cleaned_data = super(UserSettingsForm, self).clean()

        old_password = cleaned_data.get('old_password')
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        # If we don't have the old password, but we do have a new password
        # then we have an error.
        if not old_password and (password1 or password2):
            self._errors['old_password'] = self.error_class([
                'To change your password you must enter your current password.'
            ])

        if old_password:
            if not self.instance.check_password(old_password):
                self._errors['old_password'] = self.error_class([
                    self.error_messages['password_incorrect'],
                ])

        password_errors = []

        if password1 and password2 and old_password:
            if password1 != password2:
                password_errors.append("The two password fields didn't match.")

        if password_errors:
            self._errors['new_password1'] = password_errors
            self._errors['new_password2'] = password_errors

        return cleaned_data

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        if self.cleaned_data['new_password1']:
            self.instance.set_password(self.cleaned_data['new_password1'])

        if commit:
            self.instance.save()

        return self.instance

    class Meta:
        model = User
        fields = ['username', 'old_password', 'new_password1', 'new_password2']


class PatreonSettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PatreonSettingsForm, self).__init__(*args, **kwargs)

        self.fields['patreon_email_address'].required = True

    class Meta:
        model = Profile
        exclude = ['user', 'patreon_level']


class StreamSettingsForm(forms.Form):

    limit_to = forms.ChoiceField(
        choices=[
            ('3', 'Last 3 games'),
            ('5', 'Last 5 games'),
            ('10', 'Last 10 games'),
            ('20', 'Last 20 games'),
            ('hour', 'Last hour'),
            ('today', 'Today'),
            ('week', 'Last week'),
            ('all', 'All time'),
            # ('session', 'This session'),  # Have a button which allows you to start / stop a session.
        ],
        initial='today',
    )

    show_wins = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_losses = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_average_goals = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_average_assists = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_average_saves = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_average_shots = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_games_played = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_win_percentage = forms.BooleanField(
        initial=False,
        required=False,
    )

    show_goal_assist_ratio = forms.BooleanField(
        label="Show goal / assist ratio",
        initial=False,
        required=False,
    )

    # Display config
    font = forms.ChoiceField(
        initial='Helvetica Neue',
        choices=[
            ("Arial", "Arial"),
            ("Arial Black", "Arial Black"),
            ("Calibri", "Calibri"),
            ("Cambria", "Cambria"),
            ("Comic Sans MS", "Comic Sans MS"),
            ("Consolas", "Consolas"),
            ("Courier New", "Courier New"),
            ("Ebrima", "Ebrima"),
            ("Furore", "Furore"),
            ("Gabriola", "Gabriola"),
            ("Gadugi", "Gadugi"),
            ("Georgia", "Georgia"),
            ("Georgia Pro", "Georgia Pro"),
            ("Gill Sans Nova", "Gill Sans Nova"),
            ("Impact", "Impact"),
            ("Leelawadee UI", "Leelawadee UI"),
            ("Lucida Console", "Lucida Console"),
            ("Malgun Gothic", "Malgun Gothic"),
            ("MV Boli", "MV Boli"),
            ("Myanmar Text", "Myanmar Text"),
            ("Nirmala UI", "Nirmala UI"),
            ("Rockwell Nova", "Rockwell Nova"),
            ("Segoe UI", "Segoe UI"),
            ("Tahoma", "Tahoma"),
            ("Times New Roman", "Times New Roman"),
            ("Trebuchet MS", "Trebuchet MS"),
            ("Verdana", "Verdana"),
        ]
    )

    custom_font = forms.CharField(
        required=False,
        help_text="If the font you wish to use isn't listed, simply enter the name of it here.",
    )

    font_size = forms.CharField(
        initial='16',
        widget=forms.TextInput(attrs={
            'type': 'range',
            'min': '10',
            'max': '72'
        }),
    )

    text_color = forms.CharField(
        initial='#ffffff',
        widget=forms.TextInput(attrs={
            'type': 'color',
        }),
    )

    transparent_background = forms.BooleanField(
        initial=True,
        required=False,
    )

    background_color = forms.CharField(
        initial='#00ff00',
        widget=forms.TextInput(attrs={
            'type': 'color',
        })
    )

    text_shadow = forms.BooleanField(
        initial=True,
        required=False,
    )
