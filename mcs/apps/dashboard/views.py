from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

# from calplus import provider as calplus_provider
# from calplus.client import Client

from dashboard import forms
from dashboard import models
from dashboard import utils


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


def list_files(request, folder_id=None):

    if not folder_id:
        folder_id = request.GET.get('folder_id')
    if not folder_id:
        folder_id = request.POST.get('folder_id')
    if folder_id:
        try:
            folder = models.File.objects.get(id=folder_id)
            url = reverse('create_folder',
                          kwargs={'folder_id': folder_id})
        except models.File.DoesNotExist as e:
            raise e
    else:
        folder = models.File.objects.get(name='root')
        url = reverse('create_root_folder')

    return render(request, 'dashboard/files.html',
                  {'folder': folder, 'url': url})


def create_folder(request, folder_id=None):
    data = dict()
    if not folder_id:
        folder_id = request.GET.get('folder_id')
    if not folder_id:
        folder_id = request.POST.get('folder_id')
    if folder_id:
        folder = models.File.objects.get(id=folder_id)
        url = reverse('create_folder',
                      kwargs={'folder_id': folder_id})
        # Add try-catch handle FolderDoesntExist exception
    else:
        # If don't get folder_id it's root
        folder = models.File.objects.get(name='root')
        url = reverse('create_root_folder')
    if request.method == 'POST':
        form = forms.CreateFolderForm(request.POST)
        if form.is_valid():
            new_folder = form.save(commit=False)
            data['form_is_valid'] = True
            if folder.contains_folder(new_folder.name):
                # Raise error Folder with this name already exists.
                pass
            else:
                new_folder.parent = folder
                # new_folder.owner = request.user
                new_folder.save()
                return redirect('files')
        else:
            data['form_is_valid'] = False
    else:
        form = forms.CreateFolderForm()

    template_name = 'dashboard/include/partial_folder_create.html'
    data['html_form'] = render_to_string(template_name,
                                         {'form': form, 'url': url},
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
