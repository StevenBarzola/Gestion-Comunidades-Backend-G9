# Gestion-Comunidades-Backend-G9

## Requisitos previos
- Python 3.10 o superior
- pip
- (Opcional) virtualenv

## 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO_BACKEND>
cd <carpeta-backend>
```

## 2. Crear y activar entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

## 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 4. Configurar variable de entorno
Crear un archivo `.env` en la raíz del proyecto y pegar lo siguiente:
```
DATABASE_URL= ########
```

> Nota: el proyecto usa Neon (PostgreSQL) como base de datos. Si Neon está en modo "auto-suspend", la primera conexión puede tardar unos segundos en despertar.

## 5. Aplicar migraciones
```bash
python manage.py migrate
```

## 6. (Opcional) Crear superusuario
```bash
python manage.py createsuperuser
```

```bash
o usar directamente este usuario y contraseña: usuario, usuario
```

## 7. Levantar el servidor
```bash
python manage.py runserver [puerto]
```

## 8. Verificar que la API funciona
Abrir en el navegador, por ejemplo:
```
http://localhost:[puerto]/api/clubes/
```

```
Para probar otros modelos cambiar clubes por: membresias, inventario, asambleas, opciones-voto o votos
```
Debe mostrarse la interfaz navegable de Django REST Framework (DRF Browsable API) con los datos o el formulario correspondiente. Si eso se ve correctamente, el backend está funcionando.

Endpoints disponibles:
| Endpoint | Descripción |
|---|---|
| `/api/clubes/` | <describir> |
| `/api/...` | <describir> |
| `/admin/` | Panel de administración de Django |

## Notas para consumir esta API desde el frontend (PHP)
- Este backend debe correr en `http://localhost:8000`.
- En el frontend, la URL base de la API debe apuntar a `http://localhost:8000/api` (ver README del frontend).
- Si el frontend corre en un puerto distinto, este backend debe tener `django-cors-headers` configurado permitiendo ese origen (ver `settings.py`, variable `CORS_ALLOWED_ORIGINS` o `CORS_ALLOW_ALL_ORIGINS`).
