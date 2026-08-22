from rest_framework import (viewsets, generics, mixins, status)
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from .models import Club, Membresia, ItemInventario, Asamblea, OpcionVoto, Voto
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ClubSerializer, MembresiaSerializer, ItemInventarioSerializer,
    AsambleaSerializer, OpcionVotoSerializer, VotoSerializer, RegistroUsuarioSerializer
)

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def perform_create(self, serializer):
        """
        Quien registra un club queda como su presidente (RN-CLUB-01).
        Sin esta regla el club nace sin nadie que pueda administrarlo:
        su creador no podria convocar asambleas ni aprobar miembros.
        """
        club = serializer.save()
        Membresia.objects.get_or_create(
            usuario=self.request.user,
            club=club,
            defaults={'rol': 'presidente'}
        )

class MembresiaViewSet(viewsets.ModelViewSet):
    queryset = Membresia.objects.all()
    serializer_class = MembresiaSerializer

    def get_queryset(self):
        """
        Aislamiento por club (HU-SEC-03): solo se ven las membresias de las
        agrupaciones a las que el usuario pertenece.
        Admite el filtro /api/membresias/?club=1 para el panel de la directiva.
        """
        queryset = Membresia.objects.select_related('club', 'usuario').all()

        mis_clubes = clubes_del_usuario(self.request.user)
        if mis_clubes is not None:
            queryset = queryset.filter(club_id__in=mis_clubes)

        club_id = self.request.query_params.get('club', None)
        if club_id:
            queryset = queryset.filter(club_id=club_id)

        rol = self.request.query_params.get('rol', None)
        if rol:
            queryset = queryset.filter(rol=rol)

        return queryset.order_by('rol', 'usuario__username')

    def perform_create(self, serializer):
        """
        Solicitud de ingreso a un club (HU-MEMB-01).

        El usuario se toma del token, y el rol se FUERZA a 'aspirante':
        de lo contrario cualquiera podria auto-asignarse 'presidente' en el
        cuerpo del POST y saltarse todos los controles de directiva.
        La aprobacion a 'miembro' la hace la directiva (HU-MEMB-02).
        """
        club = serializer.validated_data['club']

        # Un usuario no puede pertenecer dos veces al mismo club.
        # La comprobacion es explicita porque, al declarar 'usuario' como
        # read_only, DRF desactiva su UniqueTogetherValidator automatico y la
        # restriccion de la BD estallaria como IntegrityError (HTTP 500).
        if Membresia.objects.filter(usuario=self.request.user, club=club).exists():
            raise ValidationError(
                {'non_field_errors': ['Ya tienes un rol registrado en esta agrupacion.']}
            )

        # El personal de plataforma si puede asignar roles directamente.
        if self.request.user.is_staff or self.request.user.is_superuser:
            serializer.save(usuario=self.request.user)
        else:
            serializer.save(usuario=self.request.user, rol='aspirante')

    def _es_ultimo_presidente(self, membresia):
        """Un club no puede quedarse sin presidente (RN-MEMB-02)."""
        if membresia.rol != 'presidente':
            return False
        return Membresia.objects.filter(
            club=membresia.club, rol='presidente'
        ).exclude(pk=membresia.pk).count() == 0

    def perform_update(self, serializer):
        """Cambiar el rol de un miembro es potestad de la directiva del club."""
        membresia = self.get_object()
        if not es_directiva(self.request.user, membresia.club):
            raise PermissionDenied(
                'Solo la directiva del club puede modificar las membresias.'
            )

        nuevo_rol = serializer.validated_data.get('rol', membresia.rol)
        if nuevo_rol != 'presidente' and self._es_ultimo_presidente(membresia):
            raise ValidationError(
                {'rol': 'No puedes degradar al unico presidente del club. '
                        'Nombra primero a otro presidente.'}
            )

        serializer.save()

    def perform_destroy(self, instance):
        """Cada quien puede darse de baja; expulsar a otro requiere directiva."""
        es_propia = instance.usuario_id == self.request.user.id
        if not es_propia and not es_directiva(self.request.user, instance.club):
            raise PermissionDenied(
                'Solo la directiva del club puede dar de baja a otro miembro.'
            )

        if self._es_ultimo_presidente(instance):
            raise ValidationError(
                {'detail': 'No puedes eliminar al unico presidente del club. '
                           'Nombra primero a otro presidente.'}
            )

        instance.delete()

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [AllowAny] # Permite acceso sin estar logueado

# ==========================================
# Utilidades de roles (compartidas)
# ==========================================
# Roles de Membresia con autoridad para administrar un club.
ROLES_DIRECTIVA = ('presidente', 'vicepresidente', 'secretario')


def es_directiva(user, club):
    """
    True si el usuario puede administrar ese club: por ser personal de la
    plataforma, o por tener una Membresia con rol directivo en ese club.
    """
    if user.is_staff or user.is_superuser:
        return True
    return Membresia.objects.filter(
        usuario=user, club=club, rol__in=ROLES_DIRECTIVA
    ).exists()


def clubes_del_usuario(user):
    """
    IDs de los clubes donde el usuario tiene membresia.

    Devuelve None cuando el usuario es personal de plataforma, para indicar
    "sin restriccion" (ve todo). Los viewsets usan esto para aislar los datos
    de cada club: el inventario y las asambleas de una agrupacion no deben
    ser visibles para quien no pertenece a ella (HU-SEC-03).
    """
    if user.is_staff or user.is_superuser:
        return None
    return list(
        Membresia.objects.filter(usuario=user).values_list('club_id', flat=True)
    )


class PerfilUsuarioView(APIView):
    """
    GET /api/perfil/

    Devuelve la identidad del portador del token y sus membresias, para que
    el frontend sepa que opciones mostrar (por ejemplo, el boton de crear
    asamblea solo se muestra a quien es directiva de algun club).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membresias = Membresia.objects.filter(
            usuario=request.user
        ).select_related('club')

        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'is_staff': request.user.is_staff or request.user.is_superuser,
            'membresias': [{
                'club_id': m.club.id,
                'club_nombre': m.club.nombre,
                'club_siglas': m.club.siglas,
                'rol': m.rol,
                'es_directiva': m.rol in ROLES_DIRECTIVA,
                'puede_votar': m.rol != 'aspirante',
            } for m in membresias],
        })

#==============================
# PARTE DE JULIO: Inventario
#============================== 
class ItemInventarioViewSet(viewsets.ModelViewSet):
    queryset = ItemInventario.objects.all()
    serializer_class = ItemInventarioSerializer

    def get_queryset(self):
        queryset = ItemInventario.objects.all()

        # Aislamiento por club (HU-SEC-03): solo se ve el inventario de las
        # agrupaciones a las que el usuario pertenece.
        mis_clubes = clubes_del_usuario(self.request.user)
        if mis_clubes is not None:
            queryset = queryset.filter(club_id__in=mis_clubes)

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

    def get_queryset(self):
        """
        Aislamiento por club (HU-SEC-03): solo se ven las asambleas de las
        agrupaciones a las que el usuario pertenece. Un acceso directo por ID
        a la asamblea de otro club devuelve 404, no 403, para no revelar
        siquiera que existe.
        """
        queryset = Asamblea.objects.all()
        mis_clubes = clubes_del_usuario(self.request.user)
        if mis_clubes is not None:
            queryset = queryset.filter(club_id__in=mis_clubes)
        return queryset

    def perform_create(self, serializer):
        """Solo la directiva del club puede convocar una asamblea (HU-ASAM-02)."""
        club = serializer.validated_data['club']

        if not es_directiva(self.request.user, club):
            raise PermissionDenied(
                'Solo la directiva del club puede convocar una asamblea.'
            )

        fecha_cierre = serializer.validated_data.get('fecha_cierre')
        if fecha_cierre and fecha_cierre <= timezone.now():
            raise ValidationError(
                {'fecha_cierre': 'La fecha de cierre debe ser posterior a la fecha actual.'}
            )

        # Nace en borrador: se activa recien cuando tenga sus opciones cargadas.
        serializer.save(activa=False)

    def _exigir_directiva(self, asamblea):
        if not es_directiva(self.request.user, asamblea.club):
            raise PermissionDenied(
                'Solo la directiva del club puede administrar esta asamblea.'
            )

    def perform_update(self, serializer):
        self._exigir_directiva(self.get_object())
        serializer.save()

    def perform_destroy(self, instance):
        self._exigir_directiva(instance)
        if Voto.objects.filter(asamblea=instance).exists():
            raise ValidationError(
                {'detail': 'No se puede eliminar una asamblea que ya tiene votos emitidos.'}
            )
        instance.delete()

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        POST /api/asambleas/{id}/activar/
        Abre la votacion. Exige al menos 2 opciones registradas (RN-ASAM-01).
        """
        asamblea = self.get_object()
        self._exigir_directiva(asamblea)

        if asamblea.activa:
            return Response({'detail': 'Esta asamblea ya se encuentra activa.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if Voto.objects.filter(asamblea=asamblea).exists():
            return Response({'detail': 'Esta asamblea ya fue cerrada y no puede reabrirse.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if OpcionVoto.objects.filter(asamblea=asamblea).count() < 2:
            return Response(
                {'detail': 'La asamblea necesita al menos 2 opciones de voto para abrirse.'},
                status=status.HTTP_400_BAD_REQUEST)

        if asamblea.fecha_cierre and asamblea.fecha_cierre <= timezone.now():
            return Response(
                {'detail': 'La fecha de cierre ya paso. Actualizala antes de abrir la votacion.'},
                status=status.HTTP_400_BAD_REQUEST)

        asamblea.activa = True
        asamblea.save()
        return Response({'detail': 'Votacion abierta correctamente.',
                         'activa': asamblea.activa})

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """
        POST /api/asambleas/{id}/cerrar/
        Cierra la votacion de forma irreversible (RN-ASAM-03) y habilita
        la publicacion de resultados.
        """
        asamblea = self.get_object()
        self._exigir_directiva(asamblea)

        if not asamblea.activa:
            return Response({'detail': 'Esta asamblea ya se encuentra cerrada.'},
                            status=status.HTTP_400_BAD_REQUEST)

        asamblea.activa = False
        asamblea.save()
        return Response({'detail': 'Votacion cerrada. Los resultados ya estan disponibles.',
                         'activa': asamblea.activa})

    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        """
        GET /api/asambleas/{id}/resultados/

        Devuelve el conteo agregado de votos por opcion, calculado en el
        servidor con annotate(Count(...)) del ORM. Nunca expone votos
        individuales ni la identidad de los votantes (RN-VOTO-03).

        Solo disponible cuando la asamblea ya esta cerrada, para no
        influir en una votacion en curso.
        """
        asamblea = self.get_object()

        if asamblea.activa:
            return Response(
                {'detail': 'Los resultados solo estan disponibles una vez cerrada la asamblea.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Una sola consulta agregada: cuenta los votos de cada opcion.
        opciones = (
            OpcionVoto.objects
            .filter(asamblea=asamblea)
            .annotate(total_votos=Count('voto'))
            .order_by('-total_votos', 'nombre_lista')
        )

        total = sum(o.total_votos for o in opciones)

        resultados = [{
            'opcion_id': o.id,
            'nombre_lista': o.nombre_lista,
            'descripcion': o.descripcion,
            'votos': o.total_votos,
            'porcentaje': round((o.total_votos / total) * 100, 1) if total else 0.0,
        } for o in opciones]

        return Response({
            'asamblea_id': asamblea.id,
            'titulo': asamblea.titulo,
            'activa': asamblea.activa,
            'total_votos': total,
            'resultados': resultados,
        })

class OpcionVotoViewSet(viewsets.ModelViewSet):
    queryset = OpcionVoto.objects.all()
    serializer_class = OpcionVotoSerializer

    def get_queryset(self):
        """Permite filtrar las opciones por asamblea: /api/opciones-voto/?asamblea=1"""
        queryset = OpcionVoto.objects.all()

        # Aislamiento por club (HU-SEC-03): las papeletas de otras
        # agrupaciones no son visibles.
        mis_clubes = clubes_del_usuario(self.request.user)
        if mis_clubes is not None:
            queryset = queryset.filter(asamblea__club_id__in=mis_clubes)

        asamblea_id = self.request.query_params.get('asamblea', None)
        if asamblea_id:
            queryset = queryset.filter(asamblea_id=asamblea_id)
        return queryset

    def _validar_edicion(self, asamblea):
        """
        La papeleta solo la edita la directiva, y solo mientras la eleccion
        no haya empezado: una vez emitido el primer voto queda congelada
        para no alterar las reglas a mitad de la votacion (RN-ASAM-02).
        """
        if not es_directiva(self.request.user, asamblea.club):
            raise PermissionDenied(
                'Solo la directiva del club puede editar la papeleta de esta asamblea.'
            )
        if Voto.objects.filter(asamblea=asamblea).exists():
            raise ValidationError(
                {'detail': 'La papeleta no puede modificarse: la asamblea ya tiene votos emitidos.'}
            )

    def perform_create(self, serializer):
        self._validar_edicion(serializer.validated_data['asamblea'])
        serializer.save()

    def perform_update(self, serializer):
        self._validar_edicion(self.get_object().asamblea)
        serializer.save()

    def perform_destroy(self, instance):
        self._validar_edicion(instance.asamblea)
        instance.delete()

class VotoViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Urna electoral. Deliberadamente NO es un ModelViewSet:

    - No expone retrieve/update/partial_update/destroy, porque un voto
      emitido es inmutable (RN-VOTO-02). PUT/PATCH/DELETE responden 405.
    - El listado se restringe a los votos del propio solicitante, de modo
      que nadie pueda averiguar por quien voto otra persona (RN-VOTO-03).
      El conteo publico se sirve por /api/asambleas/{id}/resultados/.
    """
    serializer_class = VotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propios votos. Permite al frontend
        # saber si ya voto sin filtrar informacion de terceros.
        queryset = Voto.objects.filter(usuario=self.request.user)
        asamblea_id = self.request.query_params.get('asamblea', None)
        if asamblea_id:
            queryset = queryset.filter(asamblea_id=asamblea_id)
        return queryset

    def perform_create(self, serializer):
        asamblea = serializer.validated_data['asamblea']
        opcion = serializer.validated_data['opcion']

        # RN-VOTO-05: la opcion debe pertenecer a la asamblea indicada.
        if opcion.asamblea_id != asamblea.id:
            raise ValidationError(
                {'opcion': 'La opcion seleccionada no pertenece a esta asamblea.'}
            )

        # RN-VOTO-04: la asamblea debe estar abierta y no vencida.
        if not asamblea.activa:
            raise ValidationError(
                {'asamblea': 'Esta asamblea ya fue cerrada. No se admiten mas votos.'}
            )
        if asamblea.fecha_cierre and timezone.now() > asamblea.fecha_cierre:
            raise ValidationError(
                {'asamblea': 'El plazo de votacion de esta asamblea ya vencio.'}
            )

        # Solo miembros activos del club votan; los aspirantes no.
        membresia = Membresia.objects.filter(
            usuario=self.request.user, club=asamblea.club
        ).first()
        if membresia is None:
            raise ValidationError(
                {'detail': 'No perteneces al club que convoco esta asamblea.'}
            )
        if membresia.rol == 'aspirante':
            raise ValidationError(
                {'detail': 'Tu membresia aun no ha sido aprobada, por lo que no puedes votar.'}
            )

        # RN-VOTO-01: un usuario, un voto por asamblea.
        # Esta comprobacion es necesaria porque al declarar 'usuario' como
        # read_only, DRF desactiva su UniqueTogetherValidator automatico y la
        # restriccion de la BD estallaria como IntegrityError (HTTP 500).
        # Se responde con la clave 'non_field_errors' que el frontend ya espera.
        if Voto.objects.filter(asamblea=asamblea, usuario=self.request.user).exists():
            raise ValidationError(
                {'non_field_errors': ['Ya emitiste tu voto en esta asamblea.']}
            )

        # El usuario se toma del token, nunca del cuerpo de la peticion.
        serializer.save(usuario=self.request.user)