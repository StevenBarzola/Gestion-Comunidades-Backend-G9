from rest_framework import (viewsets, generics)
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import Club, Membresia, ItemInventario, Asamblea, OpcionVoto, Voto
from .serializers import (
    ClubSerializer, MembresiaSerializer, ItemInventarioSerializer,
    AsambleaSerializer, OpcionVotoSerializer, VotoSerializer, RegistroUsuarioSerializer
)

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

class MembresiaViewSet(viewsets.ModelViewSet):
    queryset = Membresia.objects.all()
    serializer_class = MembresiaSerializer

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [AllowAny] # Permite acceso sin estar logueado

#==============================
# PARTE DE JULIO: Inventario
#============================== 
class ItemInventarioViewSet(viewsets.ModelViewSet):
    queryset = ItemInventario.objects.all()
    serializer_class = ItemInventarioSerializer

# ==========================================
# PARTE DE ISAAC: Asambleas y Votaciones
# ==========================================
class AsambleaViewSet(viewsets.ModelViewSet):
    queryset = Asamblea.objects.all()
    serializer_class = AsambleaSerializer

class OpcionVotoViewSet(viewsets.ModelViewSet):
    queryset = OpcionVoto.objects.all()
    serializer_class = OpcionVotoSerializer

class VotoViewSet(viewsets.ModelViewSet):
    queryset = Voto.objects.all()
    serializer_class = VotoSerializer