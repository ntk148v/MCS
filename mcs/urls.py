from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^auth/', include('authentication.urls')),
    url(r'^', include('dashboard.urls'))
]
