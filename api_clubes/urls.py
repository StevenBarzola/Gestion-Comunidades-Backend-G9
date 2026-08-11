from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClubViewSet, MembresiaViewSet, ItemInventarioViewSet

# El router genera automáticamente las rutas para el CRUD
router = DefaultRouter()
router.register(r'clubes', ClubViewSet)
router.register(r'membresias', MembresiaViewSet)
router.register(r'inventario', ItemInventarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

