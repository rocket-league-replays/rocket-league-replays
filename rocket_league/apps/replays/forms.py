from django import forms
from django.utils.safestring import mark_safe

from .models import Replay
from ...utils.replay_parser import ReplayParser


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
