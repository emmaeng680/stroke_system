from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stroke_app.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('api.urls')),
    # Default redirect to dashboard
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)