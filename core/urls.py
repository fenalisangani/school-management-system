from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core.views import ToggleLoginView, dashboard

# Rebrand the Django admin panel for the School Management System.
admin.site.site_header = 'School Management System'
admin.site.site_title = 'School Management System Admin'
admin.site.index_title = 'Administration Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'login/',
        ToggleLoginView.as_view(),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard, name='dashboard'),
    path('classes/', include('classes.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('fees/', include('fees.urls')),
    path('attendance/', include('attendance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
