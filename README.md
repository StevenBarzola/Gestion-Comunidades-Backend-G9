# Gestion-Comunidades-Backend-G9

API REST del proyecto **Plataforma web para la gestión centralizada de agrupaciones y clubes estudiantiles de la ESPOL**, desarrollada con Django y Django REST Framework.

## Requisitos previos
- Python 3.10 o superior
- pip
- (Opcional) virtualenv

## 1. Clonar el repositorio
```bash
git clone https://github.com/StevenBarzola/Gestion-Comunidades-Backend-G9.git
cd Gestion-Comunidades-Backend-G9
```

## 2. Crear y activar entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

> En macOS y algunas distribuciones de Linux los comandos son `python3` y `pip3`.

## 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 4. Configurar variable de entorno
Crear un archivo `.env` en la raíz del proyecto, tomando como base el archivo `.env.example`:

```bash
cp .env.example .env
```

Luego editar `.env` y colocar la cadena de conexión real:

```
DATABASE_URL=postgresql://usuario:contrasena@host.neon.tech/neondb?sslmode=require
```

> **Importante:** el archivo `.env` está excluido del repositorio mediante `.gitignore` y **nunca debe subirse a GitHub**. Solicita la cadena de conexión a un integrante del equipo.

> **Nota:** el proyecto usa Neon (PostgreSQL) como base de datos. Si Neon está en modo *auto-suspend*, la primera conexión puede tardar unos segundos en despertar.

## 5. Aplicar migraciones
```bash
python manage.py migrate
```

## 6. Crear superusuario
```bash
python manage.py createsuperuser
```

```bash
o usar directamente este usuario y contraseña: usuario, usuario
```

El superusuario permite acceder al panel `/admin/` y, dentro de la aplicación, administrar cualquier club sin necesidad de una membresía previa.

## 7. Levantar el servidor
```bash
python manage.py runserver
```

Por defecto queda disponible en `http://localhost:8000`.

## 8. Verificar que la API funciona
Abrir en el navegador:

```
http://localhost:8000/api/clubes/
```

Debe mostrarse la interfaz navegable de Django REST Framework (*DRF Browsable API*). Como la API exige autenticación, primero hay que iniciar sesión con el botón **Log in** que aparece en la esquina superior derecha.

---

## Endpoints disponibles

### Autenticación y cuenta
| Endpoint | Métodos | Descripción |
|---|---|---|
| `/api/registro/` | POST | Registro de un nuevo usuario. Acceso público. |
| `/api/login/` | POST | Devuelve el token de autenticación. Acceso público. |
| `/api/perfil/` | GET | Datos del usuario autenticado, con sus membresías y rol en cada club. |

### Clubes y membresías
| Endpoint | Métodos | Descripción |
|---|---|---|
| `/api/clubes/` | GET, POST | Directorio de agrupaciones. Quien crea un club queda como su presidente. |
| `/api/clubes/{id}/` | GET, PUT, DELETE | Detalle del club, incluida su nómina de integrantes. |
| `/api/membresias/` | GET, POST | Solicitar ingreso a un club. Toda solicitud se registra como `aspirante`. |
| `/api/membresias/{id}/` | PUT, DELETE | Aprobar aspirantes, asignar roles o dar de baja. Solo la directiva del club. |

Filtros disponibles: `?club=` y `?rol=`

### Inventario
| Endpoint | Métodos | Descripción |
|---|---|---|
| `/api/inventario/` | GET, POST | Catálogo de bienes de los clubes del usuario. |
| `/api/inventario/{id}/` | GET, PUT, DELETE | Detalle, edición y baja de un ítem. |

Filtros disponibles: `?club=` y `?estado=` (`Disponible` / `Prestado`)

### Asambleas y votaciones
| Endpoint | Métodos | Descripción |
|---|---|---|
| `/api/asambleas/` | GET, POST | Asambleas de los clubes del usuario. Solo la directiva puede convocarlas. |
| `/api/asambleas/{id}/activar/` | POST | Abre la votación. Requiere al menos 2 opciones registradas. |
| `/api/asambleas/{id}/cerrar/` | POST | Cierra la votación de forma irreversible y habilita los resultados. |
| `/api/asambleas/{id}/resultados/` | GET | Conteo y porcentajes por opción. Solo si la asamblea está cerrada. |
| `/api/opciones-voto/` | GET, POST | Opciones de la papeleta. Se congelan al emitirse el primer voto. |
| `/api/votos/` | GET, POST | Emitir voto. El listado solo devuelve los votos del propio usuario. |

Filtro disponible en `/api/opciones-voto/` y `/api/votos/`: `?asamblea=`

### Administración
| Endpoint | Descripción |
|---|---|
| `/admin/` | Panel de administración de Django. Requiere un usuario con permisos de staff. |

---

## Autenticación

Todos los recursos de la API exigen autenticación, salvo `/api/registro/` y `/api/login/`.

1. Obtener el token:

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "TU_USUARIO", "password": "TU_CLAVE"}'
```

2. Incluirlo en cada petición:

```bash
curl http://localhost:8000/api/asambleas/ \
  -H "Authorization: Token TU_TOKEN"
```

Una petición sin token válido recibe `401 Unauthorized`.

## Roles y permisos

Los roles se asignan por club mediante el modelo `Membresia`, de modo que un mismo usuario puede ser presidente de una agrupación y miembro de otra.

| Rol | Puede |
|---|---|
| `presidente`, `vicepresidente`, `secretario` | Convocar y cerrar asambleas, configurar la papeleta, aprobar aspirantes y asignar roles |
| `coor_eventos`, `coor_rsocial`, `miembro` | Consultar la información del club y votar en sus asambleas |
| `aspirante` | Solo consultar. **No puede votar** hasta que la directiva apruebe su ingreso |

Reglas de negocio aplicadas por el backend:

- Un usuario emite **un único voto por asamblea**; el voto es secreto e inmutable.
- Nadie puede consultar por qué opción votó otro usuario; solo se exponen los conteos agregados.
- Una asamblea nace en **borrador**, se abre explícitamente y su cierre es **irreversible**.
- Un club **no puede quedarse sin presidente**.
- Cada usuario solo accede al inventario, asambleas y membresías de los clubes a los que pertenece.

## Notas para consumir esta API desde el frontend (PHP)

- Este backend debe correr en `http://localhost:8000`.
- En el frontend, la constante `API_BASE_URL` (en `config/api.php`) debe apuntar a `http://localhost:8000/api/`.
- Si el frontend corre en un puerto distinto, revisar la configuración de `django-cors-headers` en `settings.py` (`CORS_ALLOWED_ORIGINS` o `CORS_ALLOW_ALL_ORIGINS`).
- El frontend debe iniciar sesión mediante `/api/login/` y enviar el token en la cabecera `Authorization` de cada petición posterior.