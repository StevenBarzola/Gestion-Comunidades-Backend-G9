from rest_framework import serializers
from .models import Club, Membresia, ItemInventario, Asamblea, OpcionVoto, Voto

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

# ==========================================
# PARTE DE ISAAC: Asambleas y Votaciones
# ==========================================
class AsambleaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asamblea
        fields = '__all__'

class OpcionVotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionVoto
        fields = '__all__'

class VotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voto
        fields = '__all__'