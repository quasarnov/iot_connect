"""
URL configuration for iot_connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from iot_device.views import register, activate, home, create_or_edit_device, delete_device,display_measurements,get_measurements,settings_page,receive_iot_data


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='iot_device/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('device/', create_or_edit_device, name='create_device'),
    path('device/<int:device_id>/', create_or_edit_device, name='edit_device'),
    path('device/delete/<int:device_id>/', delete_device, name='delete_device'),
    path('measurements/<int:device_id>/', display_measurements, name='display_measures'),
    path('api/measurements/<str:serial>/<str:start_date>/<str:end_date>/', get_measurements, name='api_get_measurements'),
    path('settings/', settings_page, name='settings'),
    path('api/receive-iot/', receive_iot_data, name='receive_iot_data'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)