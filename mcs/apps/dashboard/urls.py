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
        TemplateView.as_view(template_name='dashboard/files.html'),
        name='files'),
    url(r'^files/upload/$',
        views.file_upload, name='file_upload'),
    url(r'^settings/$',
        TemplateView.as_view(template_name='dashboard/settings.html'),
        name='settings'),
    url(r'^user/$',
        TemplateView.as_view(template_name='dashboard/user.html'),
        name='user'),
]
