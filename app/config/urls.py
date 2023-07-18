# django default routing
from django.contrib import admin
from django.urls import path, include
from config.index_views import index
# DJANGO_SETTINGS_MODULE chk from env
import os
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', index, name='pms_index'),
    path('admin/', admin.site.urls),
    path('managers/', include('managers.urls')),
    path('estimate/', include('estimate.urls')),
]

# dev env: Static url add
if os.getenv("DJANGO_SETTINGS_MODULE") == "config.settings.debug":
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
