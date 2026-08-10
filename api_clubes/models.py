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


# ==========================================
# 3. PARTE DE ISAAC: Asambleas y Votaciones
# ==========================================

