from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('projectapp.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')), # FOR GOOGLE SIGN IN #
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)