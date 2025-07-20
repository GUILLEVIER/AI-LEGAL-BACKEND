# Generador de Documentos Interactivo

Un sistema completo para crear documentos de forma interactiva usando React y Django. Permite subir documentos (PDF, imágenes, texto), extraer su contenido, crear plantillas con campos dinámicos y generar documentos finales.

## Características

- **Subida de documentos**: Soporta PDF, imágenes (JPG, PNG, GIF) y archivos de texto
- **Extracción de texto**: Usa pdfplumber para PDFs y OCR para imágenes
- **Editor interactivo**: QuillJS para seleccionar texto y asignar campos dinámicos
- **Plantillas**: Crear y guardar plantillas con variables {{campo}}
- **Generación de documentos**: Rellenar plantillas con datos y generar documentos finales
- **Interfaz moderna**: Diseño responsive con Tailwind CSS

## Arquitectura

### Backend (Django)
- **API REST** con Django REST Framework
- **Modelos**: DocumentoSubido, CampoDisponible, PlantillaDocumento, CampoPlantilla, DocumentoGenerado
- **Extracción de texto**: pdfplumber para PDFs, pytesseract para OCR
- **Base de datos**: SQLite (desarrollo)

### Frontend (React + TypeScript)
- **Componentes modulares**: SubirDocumento, EditorDocumento, GenerarDocumento
- **Editor rico**: QuillJS para selección de texto y asignación de campos
- **Tipos TypeScript**: Interfaces completas para todos los modelos
- **Estilos**: Tailwind CSS para diseño moderno y responsive

## Instalación

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- npm o yarn

### Backend

1. **Navegar al directorio backend**:
```bash
cd document-generator/backend
```

2. **Crear entorno virtual**:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crear superusuario** (opcional):
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor**:
```bash
python manage.py runserver
```

El backend estará disponible en `http://localhost:8000`

### Frontend

1. **Navegar al directorio frontend**:
```bash
cd document-generator/frontend
```

2. **Instalar dependencias**:
```bash
npm install --legacy-peer-deps
```

3. **Ejecutar aplicación**:
```bash
npm start
```

El frontend estará disponible en `http://localhost:3000`

## Uso

### Flujo de trabajo

1. **Subir documento**: Selecciona un archivo PDF, imagen o texto
2. **Editar documento**: Usa el editor para seleccionar texto y asignar campos dinámicos
3. **Crear plantilla**: Guarda el documento como plantilla con variables
4. **Generar documento**: Selecciona una plantilla y proporciona los datos

### API Endpoints

#### Documentos
- `POST /api/documentos-subidos/subir_documento/` - Subir documento
- `GET /api/documentos-subidos/` - Listar documentos

#### Campos
- `GET /api/campos-disponibles/` - Listar campos disponibles
- `POST /api/campos-disponibles/` - Crear nuevo campo

#### Plantillas
- `GET /api/plantillas/` - Listar plantillas
- `POST /api/plantillas/crear_plantilla/` - Crear plantilla
- `POST /api/plantillas/{id}/generar_documento/` - Generar documento

#### Documentos Generados
- `GET /api/documentos-generados/` - Listar documentos generados

## Estructura del Proyecto

```
document-generator/
├── backend/
│   ├── document_generator/     # Configuración Django
│   ├── documentos/            # App principal
│   │   ├── models.py         # Modelos de base de datos
│   │   ├── views.py          # Vistas API
│   │   ├── serializers.py    # Serializers
│   │   └── urls.py           # URLs de la app
│   ├── requirements.txt      # Dependencias Python
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── services/         # Servicios API
│   │   ├── types/           # Tipos TypeScript
│   │   └── App.tsx          # Componente principal
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Modelos de Base de Datos

### DocumentoSubido
- Almacena información de documentos subidos
- Incluye tipo (PDF, imagen, texto) y URL del archivo

### CampoDisponible
- Define campos que pueden ser asignados
- Tipos: texto, fecha, número

### PlantillaDocumento
- Plantillas con HTML y variables {{campo}}
- Relacionada con campos asignados

### CampoPlantilla
- Relación entre plantillas y campos
- Define variables dinámicas

### DocumentoGenerado
- Documentos finales generados
- Almacena datos rellenados y HTML resultante

## Tecnologías Utilizadas

### Backend
- **Django 5.2.4**: Framework web
- **Django REST Framework**: API REST
- **pdfplumber**: Extracción de texto de PDFs
- **pytesseract**: OCR para imágenes
- **Pillow**: Procesamiento de imágenes
- **SQLite**: Base de datos

### Frontend
- **React 19**: Biblioteca de UI
- **TypeScript**: Tipado estático
- **React Router**: Navegación
- **React Quill**: Editor de texto rico
- **Axios**: Cliente HTTP
- **Tailwind CSS**: Framework de estilos

## Desarrollo

### Agregar nuevos tipos de campos
1. Modificar `CampoDisponible.TIPO_DATO_CHOICES` en `models.py`
2. Actualizar tipos TypeScript en `frontend/src/types/index.ts`
3. Actualizar componentes del frontend para manejar el nuevo tipo

### Extender funcionalidad de extracción
1. Agregar nuevos métodos en `views.py`
2. Actualizar lógica de detección de tipo de archivo
3. Probar con diferentes formatos

### Personalizar estilos
1. Modificar `tailwind.config.js` para temas personalizados
2. Agregar clases CSS personalizadas en `index.css`
3. Usar clases de Tailwind en componentes

## Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad
3. Commit cambios
4. Push a la rama
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. 