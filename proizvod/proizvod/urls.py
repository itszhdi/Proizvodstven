from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('regandaut.urls')),
    path('', include('mainpage.urls')),
    path('', include('eventpage.urls')),
    path('', include('figuration.urls')),
    path('', include('userpage.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
