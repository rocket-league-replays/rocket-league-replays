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
