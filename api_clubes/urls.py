from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClubViewSet, MembresiaViewSet, ItemInventarioViewSet,
    AsambleaViewSet, OpcionVotoViewSet, VotoViewSet, RegistroUsuarioView,
    PerfilUsuarioView
)

# El router genera automáticamente las rutas para el CRUD
router = DefaultRouter()
router.register(r'clubes', ClubViewSet)
router.register(r'membresias', MembresiaViewSet)
router.register(r'inventario', ItemInventarioViewSet)
router.register(r'asambleas', AsambleaViewSet)
router.register(r'opciones-voto', OpcionVotoViewSet)
# VotoViewSet no declara .queryset (lo resuelve por usuario en get_queryset),
# por eso el router necesita un basename explicito.
router.register(r'votos', VotoViewSet, basename='voto')

urlpatterns = [
    path('', include(router.urls)),
    path('registro/', RegistroUsuarioView.as_view()),
    path('perfil/', PerfilUsuarioView.as_view()),
]

