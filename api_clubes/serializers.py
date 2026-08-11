from rest_framework import serializers
from .models import Club, Membresia, ItemInventario

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = '__all__'

class MembresiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membresia
        fields = '__all__'


#==============================
# PARTE DE JULIO: Inventario
#============================== 
class ItemInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemInventario
        fields = '__all__'
