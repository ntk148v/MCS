from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

# from calplus import provider as calplus_provider
# from calplus.client import Client

from dashboard.forms import CreateFolderForm, UploadObjectData
from dashboard.models import File
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
            folder = File.objects.get(id=folder_id)
            url = reverse('create_folder',
                          kwargs={'folder_id': folder_id})
        except File.DoesNotExist as e:
            raise e
    else:
        # Check if root doesn't exist, create it
        try:
            folder = File.objects.get(name='root')
        except File.DoesNotExist:
            # TODO: When we have User, set `owner` field
            # folder = File.objects.create(name='root',
            #                              is_root=True,
            #                              is_folder=True
            #                              owner=<current_user>)
            folder = File.objects.create(name='root',
                                         is_root=True,
                                         is_folder=True)
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
        # TODO: Add try-except handle File.DoesntExist exception
        folder = File.objects.get(id=folder_id)
        url = reverse('create_folder',
                      kwargs={'folder_id': folder_id})
    else:
        # If don't get folder_id, it's root
        # And if doen't have root folder, create it
        try:
            folder = File.objects.get(name='root')
        except File.DoesNotExist:
            folder = File.objects.create(name='root',
                                         is_root=True,
                                         is_folder=True,
                                         path='/rfolder/')
        url = reverse('create_root_folder')
    if request.method == 'POST':
        form = CreateFolderForm(request.POST)
        if form.is_valid():
            new_folder = form.save(commit=False)
            data['form_is_valid'] = True
            if folder.contains_folder(new_folder.name):
                # TODO: Raise error Folder with this name already exists.
                # Send error to form.
                pass
            else:
                new_folder.parent = folder
                # new_folder.owner = request.user
                new_folder.path = folder.path + str(new_folder.name)
                new_folder.save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            data['form_is_valid'] = False
    else:
        form = CreateFolderForm()

    template_name = 'dashboard/include/partial_folder_create.html'
    data['html_form'] = render_to_string(template_name,
                                         {'form': form, 'url': url},
                                         request=request)
    return JsonResponse(data)


def delete_files(request):
    data = dict()
    files = File.objects.filter(
        id__in=request.POST.getlist('checked_file'))
    data['form_is_valid'] = True
    if request.method == 'POST':
        files.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        template_name = 'dashboard/include/partial_files_delete.html'
        data['html_form'] = render_to_string(template_name,
                                             {'files': files},
                                             request=request)
    return JsonResponse(data)


def upload_file(request):
    if request.method == 'POST':
        form = UploadObjectData(request.POST, request.FILES)
        form.save()
        utils.handle_uploaded_file(request.FILES['data'])
        return redirect('files')
    else:
        form = UploadObjectData()
    return save_file_form(request, form,
                          'dashboard/include/partial_file_upload.html')
