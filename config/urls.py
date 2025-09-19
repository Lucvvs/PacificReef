from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hotel.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
     path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page=reverse_lazy('home')),
        name='logout'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)