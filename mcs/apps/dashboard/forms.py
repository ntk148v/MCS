from django import forms
from dashboard.models import ObjectData


class UploadObjectData(forms.ModelForm):

    class Meta:
        model = ObjectData
        fields = ('data',)


class CreateFolder(forms.Form):

    name = forms.CharField(required=True)

    # the new bit we're adding
    def __init__(self, *args, **kwargs):
        super(CreateFolder, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Folder name'
