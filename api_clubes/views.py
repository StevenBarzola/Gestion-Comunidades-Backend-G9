from rest_framework import viewsets
from .models import Club, Membresia, ItemInventario
from .serializers import ClubSerializer, MembresiaSerializer, ItemInventarioSerializer

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

class MembresiaViewSet(viewsets.ModelViewSet):
    queryset = Membresia.objects.all()
    serializer_class = MembresiaSerializer

#==============================
# PARTE DE JULIO: Inventario
#============================== 
class ItemInventarioViewSet(viewsets.ModelViewSet):
    queryset = ItemInventario.objects.all()
    serializer_class = ItemInventarioSerializer