# Opciones para Integrar React con Django

## Opción 1: Redirección Simple (IMPLEMENTADA)
**Uso**: Cuando React está en un servidor separado (desarrollo o producción)

```python
def redirect_to_react(request):
    """Redirige a la aplicación React"""
    react_url = "http://localhost:3000"  # desarrollo
    # react_url = "https://tu-dominio-react.com"  # producción
    return HttpResponseRedirect(react_url)

urlpatterns = [
    re_path(r'^$', redirect_to_react, name='home'),
    # ... resto de URLs
]
```

## Opción 2: Servir Archivos Estáticos de React
**Uso**: Cuando quieres servir React desde el mismo servidor Django

### Paso 1: Configurar settings.py
```python
# En settings.py
import os

# Directorio donde está el build de React
REACT_APP_DIR = os.path.join(BASE_DIR, 'frontend', 'build')

STATICFILES_DIRS = [
    os.path.join(REACT_APP_DIR, 'static'),
]

# Para servir el index.html de React
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [REACT_APP_DIR],  # Añadir esta línea
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### Paso 2: Crear vista para servir React
```python
from django.shortcuts import render

def serve_react(request):
    """Sirve la aplicación React"""
    return render(request, 'index.html')
```

### Paso 3: Configurar URLs
```python
urlpatterns = [
    re_path(r'^$', serve_react, name='home'),
    re_path(r'^(?!api|admin|docs|redoc).*$', serve_react, name='react_app'),
    # ... resto de URLs de API
]
```

## Opción 3: Usando django-cors-headers para CORS
**Uso**: Cuando React y Django están en dominios/puertos diferentes

### Instalación
```bash
pip install django-cors-headers
```

### Configuración en settings.py
```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    # ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Para producción
CORS_ALLOWED_ORIGINS = [
    "https://tu-dominio-react.com",
]

# O permitir todos los orígenes (solo para desarrollo)
# CORS_ALLOW_ALL_ORIGINS = True
```

## Opción 4: Proxy Reverso con Nginx (Producción)
**Uso**: En producción con Nginx como proxy

### Configuración Nginx
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Servir React
    location / {
        root /path/to/react/build;
        try_files $uri $uri/ /index.html;
    }

    # API de Django
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Admin de Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Recomendaciones por Entorno

### Desarrollo
- **Opción 1**: Redirección simple a localhost:3000
- **Opción 3**: CORS headers para comunicación entre puertos

### Producción
- **Opción 2**: Servir desde Django si es una aplicación pequeña
- **Opción 4**: Nginx como proxy reverso (recomendado para aplicaciones grandes)

## Configuración Actual Implementada

Actualmente tienes implementada la **Opción 1** con:
- URL raíz (`/`) redirige a React
- Admin accesible en `/admin/` y `/adminailegal/`
- APIs accesibles en sus rutas respectivas

Para cambiar la URL de React, modifica la variable `react_url` en la función `redirect_to_react`.