from django.conf.urls import url
from django.views.generic import TemplateView

from mcs.apps.dashboard import views

urlpatterns = [
    url(r'^home/$',
        TemplateView.as_view(template_name='dashboard/home.html'),
        name='home'),
    url(r'^clouds/$',
        TemplateView.as_view(template_name='dashboard/clouds.html'),
        name='clouds'),
    url(r'^files/$',
        views.list_files,
        name='files'),
    url(r'^files/upload/$',
        views.upload_file, name='file_upload'),
    url(r'^files/create/$',
        views.create_folder, name='folder_create'),
    url(r'^settings/$',
        TemplateView.as_view(template_name='dashboard/settings.html'),
        name='settings'),
    url(r'^user/$',
        TemplateView.as_view(template_name='dashboard/user.html'),
        name='user'),
]
