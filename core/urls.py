from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('api_clubes.urls')),
    path('api/login/', views.obtain_auth_token),
]
