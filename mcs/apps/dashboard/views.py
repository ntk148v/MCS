from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string

# from calplus import provider as calplus_provider
# from calplus.client import Client

from dashboard import forms
# from mcs.apps.dashboard import models


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


def handle_uploaded_file(file):
    #
    # TODO:
    # choose CloudNode by Chord
    # cloud_node = models.CloudNode.objects.get(identifier=tmp)
    # _provider = calplus_provider.Provider(cloud_node.type,
    #                                      cloud_node.config)
    # _client = Client(version='1.0.0',
    #                  resource='object_storage',
    #                  provider=_provider)
    # _client.upload_object('files_container',
    #                       file['data'].name,
    #                       file['data'].content,)
    #
    pass


def file_upload(request):
    if request.method == 'POST':
        form = forms.UploadObjectData(request.POST, request.FILES)
        form.save()
        handle_uploaded_file(request.FILES['data'])
        return redirect('files')
    else:
        form = forms.UploadObjectData()
    return save_file_form(request, form,
                          'dashboard/include/partial_file_upload.html')
