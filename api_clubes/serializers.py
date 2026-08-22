from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Club, Membresia, ItemInventario, Asamblea, OpcionVoto, Voto

class MembresiaSerializer(serializers.ModelSerializer):
    # (Steven) Nombre del usuario para poder listar los integrantes de un club
    # sin que el frontend tenga que resolver el ID contra otro endpoint.
    usuario_username = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = Membresia
        fields = '__all__'
        # El usuario se toma del token en la vista, nunca del cuerpo del POST.
        read_only_fields = ['usuario']

class ClubSerializer(serializers.ModelSerializer):
    # (Steven) Integrantes anidados, usados por la vista de detalle del club.
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
    # Campos calculados de solo lectura, para que el frontend sepa en que
    # etapa esta la asamblea sin tener que consultar los votos (que son
    # secretos) ni contar las opciones por su cuenta.
    estado = serializers.SerializerMethodField()
    total_opciones = serializers.SerializerMethodField()
    club_nombre = serializers.CharField(source='club.nombre', read_only=True)

    class Meta:
        model = Asamblea
        fields = '__all__'

    def get_estado(self, obj):
        """borrador = aun no se abrio | activa = votacion en curso | cerrada = escrutinio disponible"""
        if obj.activa:
            return 'activa'
        return 'cerrada' if obj.votos.exists() else 'borrador'

    def get_total_opciones(self, obj):
        return obj.opciones.count()

class OpcionVotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionVoto
        fields = '__all__'

class VotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voto
        fields = '__all__'
        read_only_fields = ['usuario']