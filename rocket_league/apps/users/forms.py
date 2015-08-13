from django import forms
from django.contrib.auth.models import User


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


class RegistrationForm(forms.Form):

    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.

    """
    required_css_class = 'required'

    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=30,
        label="Username",
        error_messages={
            'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."
        }
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Password (again)"
    )

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError("A user with that username already exists.")
        else:
            return self.cleaned_data['username']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data
