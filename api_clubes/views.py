from rest_framework import (viewsets, generics)
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import Club, Membresia, ItemInventario, Asamblea, OpcionVoto, Voto
from rest_framework.permissions import IsAuthenticated
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

    def get_queryset(self):
        queryset = ItemInventario.objects.all()
        
        # Capturar parámetros de consulta desde la URL
        estado = self.request.query_params.get('estado', None)
        club_id = self.request.query_params.get('club', None)

        # Aplicar filtro por estado (Disponible / Prestado)
        if estado:
            queryset = queryset.filter(estado__iexact=estado)

        # Aplicar filtro por ID de club
        if club_id:
            queryset = queryset.filter(club_id=club_id)

        return queryset

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
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer): serializer.save(usuario=self.request.user)