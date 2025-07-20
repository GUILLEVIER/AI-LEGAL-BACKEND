# Inicio Rápido - Generador de Documentos

## 🚀 Inicio Rápido

### Opción 1: Script Automático
```bash
./start.sh
```

### Opción 2: Manual

#### Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

#### Frontend (Terminal 2)
```bash
cd frontend
npm start
```

## 📱 Acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Django**: http://localhost:8000/admin

## 🔧 Configuración Inicial

### Crear campos de ejemplo
```bash
cd backend
source venv/bin/activate
python manage.py crear_campos_iniciales
```

### Crear superusuario (opcional)
```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
```

## 📋 Flujo de Uso

1. **Subir Documento**: Selecciona un PDF, imagen o archivo de texto
2. **Editar**: Usa el editor para seleccionar texto y asignar campos dinámicos
3. **Crear Plantilla**: Guarda el documento como plantilla con variables
4. **Generar**: Selecciona una plantilla y proporciona los datos

## 🛠️ Solución de Problemas

### Error de dependencias React
```bash
npm install --legacy-peer-deps
```

### Error de migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error de CORS
Verificar que `CORS_ALLOW_ALL_ORIGINS=True` en `settings.py`

## 📚 Documentación Completa

Ver `README.md` para documentación detallada. 