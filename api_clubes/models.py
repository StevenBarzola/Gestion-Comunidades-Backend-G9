from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. PARTE DE STEVEN: Membresías y Directorio
# ==========================================
class Club(models.Model):
    nombre = models.CharField(max_length=200)
    siglas = models.CharField(max_length=20)
    descripcion = models.TextField()
    facultad = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} [{self.siglas}]"

class Membresia(models.Model):
    ROLES = (
        ('presidente', 'Presidente'),
        ('vicepresidente', 'Vicepresidente'),
        ('secretario', 'Secretario'),
        ('coor_eventos', 'Coordinador de Eventos'),
        ('coor_rsocial', 'Coordinador de Redes Sociales'),
        ('miembro', 'Miembro'),
        ('aspirante', 'Aspirante'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membresias')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='miembros')
    rol = models.CharField(max_length=30, choices=ROLES, default='aspirante')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'club') # Un usuario solo tiene un rol activo por club

    def __str__(self):
        return f"{self.usuario.username} - {self.rol} en {self.club.siglas}"

# ==========================================
# 2. PARTE DE JULIO: Inventario
# ==========================================
class ItemInventario(models.Model):
    ESTADOS = (
        ('Disponible', 'Disponible'),
        ('Prestado', 'Prestado'),
    )
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='inventario')
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Disponible')

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.estado})"


# ==========================================
# 3. PARTE DE ISAAC: Asambleas y Votaciones
# ==========================================
class Asamblea(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='asambleas')
    titulo = models.CharField(max_length=200)
    activa = models.BooleanField(default=True)
    fecha_cierre = models.DateTimeField()

    def __str__(self):
        estado = "Activa" if self.activa else "Cerrada"
        return f"{self.titulo} - {self.club.siglas} ({estado})"

class OpcionVoto(models.Model):
    asamblea = models.ForeignKey(Asamblea, on_delete=models.CASCADE, related_name='opciones')
    nombre_lista = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre_lista} - {self.asamblea.titulo}"

class Voto(models.Model):
    asamblea = models.ForeignKey(Asamblea, on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    opcion = models.ForeignKey(OpcionVoto, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Restricción obligatoria: un usuario = un voto válido por asamblea
        unique_together = ('asamblea', 'usuario')

    def __str__(self):
        return f"Voto de {self.usuario.username} en {self.asamblea.titulo}"
