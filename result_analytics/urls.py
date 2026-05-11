from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analytics import views as av

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', av.dashboard, name='dashboard'),
    path('analytics/', include('analytics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
