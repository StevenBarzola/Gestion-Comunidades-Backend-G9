from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Club, Membresia, ItemInventario, Asamblea, OpcionVoto, Voto

class MembresiaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Membresia
        fields = '__all__'
        read_only_fields = ['usuario']

class ClubSerializer(serializers.ModelSerializer):
    miembros = MembresiaSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = '__all__'

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password'] 
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Se usa set_password() para que Django aplique la encriptación PBKDF2
        usuario = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        usuario.set_password(validated_data['password']) 
        usuario.save()
        return usuario


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
        read_only_fields = ['usuario']