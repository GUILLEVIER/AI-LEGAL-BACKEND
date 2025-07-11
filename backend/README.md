# backend

Sistema de gestión de documentos legales basado en Django y Django REST Framework.

## Descripción
Este proyecto permite la gestión de usuarios, empresas y documentos legales, con autenticación, permisos, administración avanzada y API REST modularizada.

## Estructura de Apps
- `users`: Gestión de usuarios y autenticación.
- `companies`: Gestión de empresas y planes.
- `documents`: Gestión de documentos, plantillas, contratos, demandas, escritos, clasificaciones, etc.
- `core`: Configuración global y URLs.

## Requisitos
- Python 3.10+
- Django 4+
- Django REST Framework
- dj-rest-auth, django-allauth
- drf-yasg (Swagger)
- Otros: ver `requirements.txt`

## Instalación
1. Clona el repositorio y entra al directorio:
   ```bash
   git clone <repo_url>
   cd legalback
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Variables de entorno
Crea un archivo `.env` en la raíz con al menos:
```
SECRET_KEY=tu_clave_secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3  # O la URL de tu base de datos
```

## Migraciones y base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

## Crear superusuario
```bash
python manage.py createsuperuser
```

## Ejecución del servidor
```bash
python manage.py runserver
```

## Acceso a la administración
- Panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Solo se muestran los modelos relevantes; modelos de tokens, sitios y sociales están ocultos.

## API y documentación
- Swagger: [http://localhost:8000/docs/](http://localhost:8000/docs/)
- Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

## Tests
```bash
python manage.py test
```

## Notas de producción
- Configura correctamente `DEBUG=False`, `ALLOWED_HOSTS` y variables sensibles en `.env`.
- Ejecuta `python manage.py collectstatic` y sirve `/static/` con Nginx o similar.
- Usa HTTPS en producción.

## Docker (opcional)
Incluye un `Dockerfile` y `docker-compose.yaml` para despliegue rápido.

---

**Desarrollado por Juan Maldonado.** 