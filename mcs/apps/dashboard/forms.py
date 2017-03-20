from django import forms
from dashboard.models import ObjectData


class UploadObjectData(forms.ModelForm):

    class Meta:
        model = ObjectData
        fields = ('data',)
