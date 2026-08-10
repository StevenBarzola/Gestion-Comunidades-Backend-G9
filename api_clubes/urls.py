from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClubViewSet, MembresiaViewSet

# El router genera automáticamente las rutas para el CRUD
router = DefaultRouter()
router.register(r'clubes', ClubViewSet)
router.register(r'membresias', MembresiaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]