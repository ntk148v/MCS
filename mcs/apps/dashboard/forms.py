from django import forms
from django.contrib.admin import widgets

from dashboard.models import ObjectData, File


class UploadFile(forms.ModelForm):

    class Meta:
        model = File
        exclude = ['name', 'path', 'is_folder', 'size', 'parent_path']


class CreateFolderForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ('name', )
        widgets = {
            'name': widgets.AdminTextInputWidget,
        }


class UploadObjectData(forms.ModelForm):

    class Meta:
        model = ObjectData
        fields = ('data',)
