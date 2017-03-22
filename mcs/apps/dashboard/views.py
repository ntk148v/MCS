import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

# from calplus import provider as calplus_provider
# from calplus.client import Client

from dashboard import forms
from dashboard import utils

# from dashboard import models


def save_file_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            # Render file tree
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context,
                                         request=request)
    return JsonResponse(data)


def list_files(request):
    if request.GET.get('path'):
        _path = request.GET.get('path')
    else:
        _path = '/rfolder'
    # Get data from json
    with open('fake_data.json') as json_data:
        _fdata = json.load(json_data)
    # Init cdata as empty list
    files = []
    utils.get_folder_by_path(_fdata, _path, files)
    return render(request, 'dashboard/files.html',
                  {'files': files[0]})


def create_folder(request):
    data = dict()
    if request.method == 'POST':
        form = forms.CreateFolder(request.POST)
    else:
        form = forms.CreateFolder()
    data['form_is_valid'] = True
    template_name = 'dashboard/include/partial_folder_create.html'
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context,
                                         request=request)

    return JsonResponse(data)


def upload_file(request):
    if request.method == 'POST':
        form = forms.UploadObjectData(request.POST, request.FILES)
        form.save()
        utils.handle_uploaded_file(request.FILES['data'])
        return redirect('files')
    else:
        form = forms.UploadObjectData()
    return save_file_form(request, form,
                          'dashboard/include/partial_file_upload.html')
