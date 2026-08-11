from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClubViewSet, MembresiaViewSet, ItemInventarioViewSet
from .views import (
    ClubViewSet, MembresiaViewSet, ItemInventarioViewSet,
    AsambleaViewSet, OpcionVotoViewSet, VotoViewSet
)

# El router genera automáticamente las rutas para el CRUD
router = DefaultRouter()
router.register(r'clubes', ClubViewSet)
router.register(r'membresias', MembresiaViewSet)
router.register(r'inventario', ItemInventarioViewSet)
router.register(r'asambleas', AsambleaViewSet)
router.register(r'opciones-voto', OpcionVotoViewSet)
router.register(r'votos', VotoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

