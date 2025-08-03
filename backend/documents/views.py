import io
import pdfplumber
import pytesseract
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from rest_framework import generics, viewsets, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.table import Table
from docx.text.paragraph import Paragraph
from rest_framework.views import APIView

from core.mixins import StandardResponseMixin
from users.models import Usuarios
from users.serializers import UsuariosSerializer

from .models import (
    DocumentoSubido, 
    CampoDisponible, 
    PlantillaDocumento, 
    CampoPlantilla, 
    DocumentoGenerado,
    PlantillaFavorita,
    TipoPlantillaDocumento,
    PlantillaCompartida,
    ClasificacionPlantillaGeneral,
    PlantillaGeneral,
    PlantillaGeneralCompartida,
)
from .serializers import (
    DocumentoSubidoSerializer,
    CampoDisponibleSerializer,
    PlantillaDocumentoSerializer,
    DocumentoGeneradoSerializer,
    CrearPlantillaSerializer,
    GenerarDocumentoSerializer,
    TipoPlantillaDocumentoSerializer,
    PlantillaCompartidaSerializer,
    PlantillaFavoritaSerializer,
    ClasificacionPlantillaGeneralSerializer,
    PlantillaGeneralSerializer,
    PlantillaGeneralCompartidaSerializer,
    FileUploadSerializer,
)


class DocumentoSubidoViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = DocumentoSubido.objects.all()
    serializer_class = DocumentoSubidoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def list(self, request, *args, **kwargs):
        """Listar documentos subidos sin paginación"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Documentos subidos obtenidos exitosamente",
                code="documents_retrieved",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener documentos subidos",
                code="documents_error",
                http_status=500
            )
    
    def create(self, request, *args, **kwargs):
        """Crear documento subido con formato estándar"""
        return self.standard_create_response(
            request=request,
            success_message="Documento subido exitosamente",
            code="document_created",
            error_message="Error al subir documento",
            error_code="document_create_error"
        )

    @action(detail=False, methods=['post'])
    def subir_documento(self, request):
        """Subir documento y extraer texto"""
        try:
            archivo = request.FILES.get('archivo')
            if not archivo:
                return self.error_response(
                    errors="No se proporcionó archivo",
                    message="Archivo requerido",
                    code="missing_file",
                    http_status=400
                )

            # Determinar tipo de archivo
            nombre_archivo = archivo.name.lower()
            if nombre_archivo.endswith('.pdf'):
                tipo = 'pdf'
            elif nombre_archivo.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                tipo = 'imagen'
            elif nombre_archivo.endswith('.docx'):
                tipo = 'word'
            else:
                tipo = 'texto'

            # Guardar archivo
            ruta_archivo = f'documentos/{archivo.name}'
            ruta_completa = default_storage.save(ruta_archivo, ContentFile(archivo.read()))

            # Extraer texto según el tipo
            texto_extraido = ""
            if tipo == 'pdf':
                texto_extraido = self._extraer_texto_pdf(archivo)
            elif tipo == 'imagen':
                texto_extraido = self._extraer_texto_imagen(archivo)
            elif tipo == 'word':
                # Guardar archivo temporalmente para python-docx
                archivo.seek(0)
                doc = docx.Document(archivo)
                texto_extraido = self._extraer_texto_docx(doc)
            else:
                archivo.seek(0)
                texto_extraido = archivo.read().decode('utf-8')
                print(texto_extraido)

            # Verificar autenticación
            if not request.user.is_authenticated:
                return self.error_response(
                    errors="Usuario no autenticado",
                    message="Autenticación requerida",
                    code="authentication_required",
                    http_status=401
                )
            
            # Crear registro en base de datos
            documento = DocumentoSubido.objects.create(
                usuario=request.user,
                nombre_original=archivo.name,
                tipo=tipo,
                archivo_url=ruta_completa
            )

            # Preparar datos de respuesta
            data = {
                'id': documento.id,
                'texto_extraido': texto_extraido,
                'tipo': tipo,
                'nombre_original': archivo.name,
                'archivo_url': ruta_completa,
                'fecha_subida': documento.fecha_subida
            }

            return self.success_response(
                data=data,
                message="Documento subido y procesado exitosamente",
                code="document_uploaded",
                http_status=201
            )

        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al procesar el documento",
                code="document_processing_error",
                http_status=500
            )

    def _extraer_texto_pdf(self, archivo):
        """Extraer texto de PDF usando pdfplumber"""
        try:
            #pdf_bytes = archivo.read()
            #pdf_buffer = io.BytesIO(pdf_bytes)
            pdf = pdfplumber.open(archivo)
            result = ""
            for page in pdf.pages:
                words = page.extract_words()
                # Agrupa palabras por línea (top)
                lines = {}
                for word in words:
                    line_key = round(word['top'])
                    if line_key not in lines:
                        lines[line_key] = []
                    lines[line_key].append(word)
                for line_words in lines.values():
                    line_words.sort(key=lambda w: w['x0'])
                    prev_x1 = None
                    line = ""
                    for idx, word in enumerate(line_words):
                        if idx == 0:
                            # Primera palabra de la línea
                            n_dollars = int(word['x0'] // 5)  # Ajusta el divisor según el resultado visual
                            line += "&nbsp;" * n_dollars
                        else:
                            gap = word['x0'] - prev_x1
                            if gap > 5:
                                n_spaces = int(gap // 3)
                                line += " " * max(1, n_spaces)
                            else:
                                line += " "
                        line += word['text']
                        prev_x1 = word['x1']
                    result += line + "\n" + "<br>"
                    print(result)
            return result
        except Exception as e:
            return f"Error al extraer texto del PDF: {str(e)}"

    def _extraer_texto_imagen(self, archivo):
        """Extraer texto de imagen usando OCR"""
        try:
            imagen = Image.open(archivo)
            texto = pytesseract.image_to_string(imagen, lang='spa')
            return texto
        except Exception as e:
            return f"Error al extraer texto de la imagen: {str(e)}"

    def _extraer_texto_docx(self, doc):
        html = ""
        in_list = False
        for block in iter_block_items(doc):
            if isinstance(block, Table):
                html += "<table border='1' style='border-collapse:collapse;margin:10px 0;'>"
                for row in block.rows:
                    html += "<tr>"
                    for cell in row.cells:
                        html += f"<td>{cell.text}</td>"
                    html += "</tr>"
                html += "</table>"
            elif isinstance(block, docx.text.paragraph.Paragraph):
                p = block
                style = p.style.name.lower()
                text = p.text.replace(" ", "&nbsp;")
                align = ""
                if p.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                    align = "text-align:center;"
                elif p.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
                    align = "text-align:right;"
                elif p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                    align = "text-align:justify;"
                indent = ""
                if p.paragraph_format.first_line_indent:
                    indent += f"text-indent:{int(p.paragraph_format.first_line_indent.pt)}pt;"
                if p.paragraph_format.left_indent:
                    indent += f"margin-left:{int(p.paragraph_format.left_indent.pt)}pt;"
                style_attr = f'style="{align}{indent}"' if (align or indent) else ""
                # Detectar listas
                if is_list_paragraph(p):
                    if not in_list:
                        html += "<ul>"
                        in_list = True
                    html += f"<li {style_attr}>{text}</li>"
                else:
                    if in_list:
                        html += "</ul>"
                        in_list = False
                    if style.startswith("heading"):
                        html += f"<h2 {style_attr}>{text}</h2>"
                    else:
                        html += f"<p {style_attr}>{text}</p>"
        if in_list:
            html += "</ul>"
        html += ""
        return html
        #return HttpResponse(f"<pre>\n{html}\n</pre>", status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Obtener documento subido específico con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Documento subido obtenido exitosamente",
                code="available_field_retrieved",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el documento subido",
                code="available_field_error",
                http_status=500
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar documento subido con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Documento subido actualizado exitosamente",
                code="available_field_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el documento subido",
                code="document_uploaded_update_error",
                http_status=400
            )
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar parcialmente documento subido con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Documento subido actualizado exitosamente",
                code="available_field_partial_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el documento subido",
                code="document_uploaded_update_error",
                http_status=400
            )
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar documento subido con formato estándar"""
        try:
            instance = self.get_object()
            documento_nombre = instance.nombre  # Guardamos el nombre antes de eliminar
            instance.delete()
            return self.success_response(
                data={"deleted_document": documento_nombre},
                message="Documento subido eliminado exitosamente",
                code="document_uploaded_deleted",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al eliminar el campo disponible",
                code="available_field_delete_error",
                http_status=500
            )

class CampoDisponibleViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = CampoDisponible.objects.all()
    serializer_class = CampoDisponibleSerializer

    def list(self, request, *args, **kwargs):
        """Listar campos disponibles con formato estándar"""
        return self.paginated_list_response(
            request=request,
            queryset=self.get_queryset(),
            serializer_class=self.serializer_class,
            paginated_message="Campos disponibles obtenidos exitosamente (paginados)",
            unpaginated_message="Campos disponibles obtenidos exitosamente",
            code="available_fields_retrieved",
            error_code="available_fields_error"
        )
    
    def create(self, request, *args, **kwargs):
        """Crear campo disponible con formato estándar"""
        return self.standard_create_response(
            request=request,
            success_message="Campo disponible creado exitosamente",
            code="available_field_created",
            error_message="Error al crear campo disponible",
            error_code="available_field_creation_error"
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Obtener campo disponible específico con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Campo disponible obtenido exitosamente",
                code="available_field_retrieved",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el campo disponible",
                code="available_field_error",
                http_status=500
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar campo disponible con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Campo disponible actualizado exitosamente",
                code="available_field_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el campo disponible",
                code="available_field_update_error",
                http_status=400
            )
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar parcialmente campo disponible con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Campo disponible actualizado exitosamente",
                code="available_field_partial_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el campo disponible",
                code="available_field_update_error",
                http_status=400
            )
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar campo disponible con formato estándar"""
        try:
            instance = self.get_object()
            campo_nombre = instance.nombre  # Guardamos el nombre antes de eliminar
            instance.delete()
            return self.success_response(
                data={"deleted_field": campo_nombre},
                message="Campo disponible eliminado exitosamente",
                code="available_field_deleted",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al eliminar el campo disponible",
                code="available_field_delete_error",
                http_status=500
            )

class TipoPlantillaDocumentoViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = TipoPlantillaDocumento.objects.all()
    serializer_class = TipoPlantillaDocumentoSerializer

    def list(self, request, *args, **kwargs):
        """Listar tipos de plantilla de documento con formato estándar"""
        return self.paginated_list_response(
            request=request,
            queryset=self.get_queryset(),
            serializer_class=self.serializer_class,
            paginated_message="Tipos de plantilla de documento obtenidos exitosamente (paginados)",
            unpaginated_message="Tipos de plantilla de documento obtenidos exitosamente",
            code="template_types_retrieved",
            error_code="template_types_error"
        )
    
    def create(self, request, *args, **kwargs):
        """Crear tipo de plantilla de documento con formato estándar"""
        return self.standard_create_response(
            request=request,
            success_message="Tipo de plantilla de documento creado exitosamente",
            code="template_type_created",
            error_message="Error al crear tipo de plantilla de documento",
            error_code="template_type_creation_error"
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Obtener tipo de plantilla de documento específico con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Tipo de plantilla de documento obtenido exitosamente",
                code="template_type_retrieved",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el tipo de plantilla de documento",
                code="template_type_error",
                http_status=500
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar tipo de plantilla de documento con formato estándar"""
        try:
            response = super().update(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Tipo de plantilla de documento actualizado exitosamente",
                code="template_type_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el tipo de plantilla de documento",
                code="template_type_update_error",
                http_status=400
            )
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar parcialmente tipo de plantilla de documento con formato estándar"""
        try:
            response = super().partial_update(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Tipo de plantilla de documento actualizado exitosamente",
                code="template_type_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el tipo de plantilla de documento",
                code="template_type_update_error",
                http_status=400
            )
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar tipo de plantilla de documento con formato estándar"""
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                data=None,
                message="Tipo de plantilla de documento eliminado exitosamente",
                code="template_type_deleted",
                http_status=204
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al eliminar el tipo de plantilla de documento",
                code="template_type_delete_error",
                http_status=500
            )

class PlantillaDocumentoViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = PlantillaDocumento.objects.none()
    serializer_class = PlantillaDocumentoSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PlantillaDocumento.objects.none()
        user = self.request.user
        # Plantillas propias o compartidas conmigo
        compartidas_ids = PlantillaCompartida.objects.filter(usuario=user).values_list('plantilla_id', flat=True)
        return PlantillaDocumento.objects.filter(
            models.Q(usuario=user) | models.Q(id__in=compartidas_ids)
        ).distinct()
    
    def list(self, request, *args, **kwargs):
        print("list: ", request.user)
        """Listar plantillas con información de favoritos"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    errors="Usuario no autenticado",
                    message="Autenticación requerida",
                    code="authentication_required",
                    http_status=401
                )
            usuario = request.user
            plantillas = self.get_queryset()  # Solo las del usuario
            
            # Obtener favoritos del usuario
            favoritos_usuario = PlantillaFavorita.objects.filter(usuario=usuario).values_list('plantilla_id', flat=True)
            
            plantillas_con_favoritos = []
            for plantilla in plantillas:
                # Obtener campos asociados
                campos_asociados = []
                for campo_plantilla in plantilla.campos_asociados.all():
                    campos_asociados.append({
                        'id': campo_plantilla.id,
                        'campo': campo_plantilla.campo.id,
                        'nombre_variable': campo_plantilla.nombre_variable,
                        'campo_nombre': campo_plantilla.campo.nombre,
                        'campo_tipo': campo_plantilla.campo.tipo_dato
                    })
                
                plantilla_data = {
                    'id': plantilla.id,
                    'nombre': plantilla.nombre,
                    'descripcion': plantilla.descripcion,
                    'html_con_campos': plantilla.html_con_campos,
                    'fecha_creacion': plantilla.fecha_creacion,
                    'campos_asociados': campos_asociados,
                    'es_favorito': plantilla.id in favoritos_usuario,
                    'tipo': {
                        'id': plantilla.tipo.id,
                        'nombre': plantilla.tipo.nombre
                    } if plantilla.tipo else None
                }
                plantillas_con_favoritos.append(plantilla_data)
            
            # Usar success_response directamente en lugar de paginated_list_response
            return self.success_response(
                data=plantillas_con_favoritos,
                message="Plantillas de documentos obtenidas exitosamente",
                code="templates_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantillas de documentos: {str(e)}",
                code="templates_retrieval_error"
            )

    def create(self, request, *args, **kwargs):
        """Crear plantilla de documento"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    errors="Usuario no autenticado",
                    message="Autenticación requerida",
                    code="authentication_required",
                    http_status=401
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                plantilla = serializer.save(usuario=request.user)
                return self.standard_create_response(
                    serializer,
                    message="Plantilla de documento creada exitosamente",
                    code="template_created"
                )
            else:
                return self.error_response(
                    message="Datos inválidos para crear plantilla de documento",
                    code="template_creation_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al crear plantilla de documento: {str(e)}",
                code="template_creation_error"
            )

    def retrieve(self, request, *args, **kwargs):
        """Obtener plantilla de documento específica"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Plantilla de documento obtenida exitosamente",
                code="template_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantilla de documento: {str(e)}",
                code="template_retrieval_error"
            )

    def update(self, request, *args, **kwargs):
        """Actualizar plantilla de documento completa"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla de documento actualizada exitosamente",
                    code="template_updated"
                )
            else:
                return self.error_response(
                    message="Datos inválidos para actualizar plantilla de documento",
                    code="template_update_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar plantilla de documento: {str(e)}",
                code="template_update_error"
            )

    def destroy(self, request, *args, **kwargs):
        """Eliminar plantilla de documento"""
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                message="Plantilla de documento eliminada exitosamente",
                code="template_deleted"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al eliminar plantilla de documento: {str(e)}",
                code="template_deletion_error"
            )

    @action(detail=False, methods=['post'])
    def crear_plantilla(self, request):
        print("=== CREAR PLANTILLA ===")
        print("Request data:", request.data)
        print("Request method:", request.method)
        print("Request data:", request.data)
        """Crear plantilla con campos asociados"""
        try:
            serializer = CrearPlantillaSerializer(data=request.data)
            print("Serializer is valid:", serializer.is_valid())
            print("Serializer validated data:", serializer.validated_data if serializer.is_valid() else "Invalid")
            if serializer.is_valid():
                # Obtener el tipo si se proporciona
                tipo = None
                print(f"Tipo ID recibido: {serializer.validated_data.get('tipo_id')}")
                if 'tipo_id' in serializer.validated_data and serializer.validated_data['tipo_id']:
                    try:
                        tipo = TipoPlantillaDocumento.objects.get(id=serializer.validated_data['tipo_id'])
                        print(f"Tipo encontrado: {tipo.nombre}")
                    except TipoPlantillaDocumento.DoesNotExist:
                        print(f"Tipo no encontrado con ID: {serializer.validated_data['tipo_id']}")
                        pass

                # Verificar autenticación
                if not request.user.is_authenticated:
                    return self.error_response(
                        errors="Usuario no autenticado",
                        message="Autenticación requerida",
                        code="authentication_required",
                        http_status=401
                    )
                
                # Crear plantilla
                plantilla = PlantillaDocumento.objects.create(
                    nombre=serializer.validated_data['nombre'],
                    descripcion=serializer.validated_data.get('descripcion', ''),
                    html_con_campos=serializer.validated_data.get('html_con_campos', ''),
                    tipo=tipo,
                    usuario=request.user
                )

                # Crear campos asociados
                campos = serializer.validated_data.get('campos', [])
                for campo_data in campos:
                    CampoPlantilla.objects.create(
                        plantilla=plantilla,
                        campo_id=campo_data['campo_id'],
                        nombre_variable=campo_data['nombre_variable']
                    )

                return self.success_response(
                    data={'id': plantilla.id},
                    message="Plantilla creada exitosamente",
                    code="template_created"
                )
            else:
                print("Serializer errors:", serializer.errors)
                return self.error_response(
                    message="Datos inválidos para crear plantilla",
                    code="template_creation_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al crear plantilla: {str(e)}",
                code="template_creation_error"
            )

    @action(detail=True, methods=['post'])
    def generar_documento(self, request, pk=None):
        print("generar_documento")
        """Generar documento a partir de plantilla y datos"""
        try:
            plantilla = self.get_object()
            serializer = GenerarDocumentoSerializer(data=request.data)
            
            if serializer.is_valid():
                datos = serializer.validated_data['datos']
                
                # Reemplazar campos en el HTML
                html_resultante = plantilla.html_con_campos
                for campo_plantilla in plantilla.campos_asociados.all():
                    variable = f"{{{{{campo_plantilla.nombre_variable}}}}}"
                    valor = datos.get(campo_plantilla.nombre_variable, '')
                    html_resultante = html_resultante.replace(variable, str(valor))

                # Verificar autenticación
                if not request.user.is_authenticated:
                    return self.error_response(
                        errors="Usuario no autenticado",
                        message="Autenticación requerida",
                        code="authentication_required",
                        http_status=401
                    )
                
                # Crear documento generado
                documento = DocumentoGenerado.objects.create(
                    plantilla=plantilla,
                    usuario=request.user,
                    datos_rellenados=datos,
                    html_resultante=html_resultante
                )

                return self.success_response(
                    data={
                        'id': documento.id,
                        'html_resultante': html_resultante
                    },
                    message="Documento generado exitosamente",
                    code="document_generated"
                )
            else:
                return self.error_response(
                    message="Datos inválidos para generar documento",
                    code="document_generation_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al generar documento: {str(e)}",
                code="document_generation_error"
            )

    def partial_update(self, request, *args, **kwargs):
        print("partial_update")
        print(request)
        print(request.data)
        try:
            instance = self.get_object()
            data = request.data

            # Quitar campo asociado (flujo rápido)
            if 'quitar_campo_id' in data:
                campo_plantilla_id = data['quitar_campo_id']
                from .models import CampoPlantilla
                print(f"[LOG] Quitar campo asociado: {campo_plantilla_id}")
                CampoPlantilla.objects.filter(id=campo_plantilla_id, plantilla=instance).delete()
                return self.success_response(
                    message="Campo asociado eliminado exitosamente",
                    code="template_field_removed"
                )

            # Manejar tipo de plantilla
            if 'tipo' in data:
                tipo = None
                if data['tipo']:
                    try:
                        tipo = TipoPlantillaDocumento.objects.get(id=data['tipo'])
                    except TipoPlantillaDocumento.DoesNotExist:
                        pass
                instance.tipo = tipo
                instance.save()

            # Sincronizar campos asociados si se envía 'campos'
            if 'campos' in data:
                from .models import CampoPlantilla
                nuevos = data['campos']
                print(f"[LOG] Campos recibidos en PATCH: {nuevos}")
                nuevos_set = set((c['campo_id'], c['nombre_variable']) for c in nuevos)
                actuales = list(instance.campos_asociados.all())
                actuales_set = set((c.campo_id, c.nombre_variable) for c in actuales)

                # Eliminar los que ya no están
                for c in actuales:
                    if (c.campo_id, c.nombre_variable) not in nuevos_set:
                        print(f"[LOG] Eliminando campo asociado: {c.campo_id}, {c.nombre_variable}")
                        c.delete()

                # Agregar los nuevos que no existen
                for c in nuevos:
                    if (c['campo_id'], c['nombre_variable']) not in actuales_set:
                        print(f"[LOG] Agregando campo asociado: {c['campo_id']}, {c['nombre_variable']}")
                        CampoPlantilla.objects.create(
                            plantilla=instance,
                            campo_id=c['campo_id'],
                            nombre_variable=c['nombre_variable']
                        )

            # Resto del update normal
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla de documento actualizada exitosamente",
                    code="template_updated"
                )
            else:
                return self.error_response(
                    message="Datos inválidos para actualizar plantilla de documento",
                    code="template_update_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar plantilla de documento: {str(e)}",
                code="template_update_error"
            )

    def destroy(self, request, *args, **kwargs):
        print("destroy")
        try:
            instance = self.get_object()
            print(f"[LOG] Eliminando plantilla: {instance.id} - {instance.nombre}")
            instance.delete()
            return self.success_response(
                message="Plantilla de documento eliminada exitosamente",
                code="template_deleted"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al eliminar plantilla de documento: {str(e)}",
                code="template_deletion_error"
            )

class DocumentoGeneradoViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = DocumentoGenerado.objects.none()
    serializer_class = DocumentoGeneradoSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return DocumentoGenerado.objects.none()
        return DocumentoGenerado.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        """Asignar automáticamente el usuario logueado al crear un documento generado"""
        if not self.request.user.is_authenticated:
            raise PermissionError("Usuario no autenticado")
        serializer.save(usuario=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Listar documentos generados con formato estándar"""
        return self.paginated_list_response(
            request=request,
            queryset=self.get_queryset(),
            serializer_class=self.serializer_class,
            paginated_message="Documentos generados obtenidos exitosamente (paginados)",
            unpaginated_message="Documentos generados obtenidos exitosamente",
            code="generated_documents_retrieved",
            error_code="generated_documents_error"
        )
    
    def create(self, request, *args, **kwargs):
        """Crear documento generado con formato estándar"""
        return self.standard_create_response(
            request=request,
            success_message="Documento generado exitosamente",
            code="document_generated",
            error_message="Error al generar documento",
            error_code="document_generation_error"
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Obtener documento generado específico con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Documento generado obtenido exitosamente",
                code="generated_document_retrieved",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el documento generado",
                code="generated_document_error",
                http_status=500
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar documento generado con formato estándar"""
        try:
            response = super().update(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Documento generado actualizado exitosamente",
                code="generated_document_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el documento generado",
                code="generated_document_update_error",
                http_status=400
            )
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar parcialmente documento generado con formato estándar"""
        try:
            response = super().partial_update(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Documento generado actualizado exitosamente",
                code="generated_document_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el documento generado",
                code="generated_document_update_error",
                http_status=400
            )
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar documento generado con formato estándar"""
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                data=None,
                message="Documento generado eliminado exitosamente",
                code="generated_document_deleted",
                http_status=204
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al eliminar el documento generado",
                code="generated_document_delete_error",
                http_status=500
            )

class PlantillaFavoritaViewSet(StandardResponseMixin, viewsets.GenericViewSet):
    queryset = PlantillaFavorita.objects.none()
    serializer_class = PlantillaFavoritaSerializer
    '''
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PlantillaFavorita.objects.none()
        return PlantillaFavorita.objects.filter(usuario=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Listar favoritos del usuario con formato estándar"""
        return self.paginated_list_response(
            request=request,
            queryset=self.get_queryset(),
            serializer_class=self.serializer_class,
            paginated_message="Favoritos obtenidos exitosamente (paginados)",
            unpaginated_message="Favoritos obtenidos exitosamente",
            code="favorites_retrieved",
            error_code="favorites_error"
        )
    
    def create(self, request, *args, **kwargs):
        """Crear favorito con formato estándar"""
        return self.standard_create_response(
            request=request,
            success_message="Favorito creado exitosamente",
            code="favorite_created",
            error_message="Error al crear favorito",
            error_code="favorite_create_error"
        )
    '''
    @action(detail=False, methods=['post'])
    def agregar_favorito(self, request):
        """Agregar plantilla a favoritos"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    errors="Usuario no autenticado",
                    message="Autenticación requerida",
                    code="authentication_required",
                    http_status=401
                )
            
            plantilla_id = request.data.get('plantilla_id')
            if not plantilla_id:
                return self.error_response(
                    errors="plantilla_id es requerido",
                    message="Datos incompletos",
                    code="missing_data",
                    http_status=400
                )
            
            plantilla = PlantillaDocumento.objects.get(id=plantilla_id)
            usuario = request.user
            
            # Verificar si ya existe
            favorito, created = PlantillaFavorita.objects.get_or_create(
                usuario=usuario,
                plantilla=plantilla
            )
            
            if created:
                serializer = self.serializer_class(favorito)
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla agregada a favoritos exitosamente",
                    code="favorite_added",
                    http_status=201
                )
            else:
                serializer = self.serializer_class(favorito)
                return self.success_response(
                    data=serializer.data,
                    message="La plantilla ya está en favoritos",
                    code="favorite_exists",
                    http_status=200
                )
                
        except PlantillaDocumento.DoesNotExist:
            return self.error_response(
                errors="Plantilla no encontrada",
                message="Recurso no encontrado",
                code="not_found",
                http_status=404
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error interno del servidor",
                code="server_error",
                http_status=500
            )
    
    @action(detail=False, methods=['delete'])
    def quitar_favorito(self, request):
        """Quitar plantilla de favoritos"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    errors="Usuario no autenticado",
                    message="Autenticación requerida",
                    code="authentication_required",
                    http_status=401
                )
            
            plantilla_id = request.data.get('plantilla_id')
            if not plantilla_id:
                return self.error_response(
                    errors="plantilla_id es requerido",
                    message="Datos incompletos",
                    code="missing_data",
                    http_status=400
                )
            
            usuario = request.user
            
            favorito = PlantillaFavorita.objects.get(
                usuario=usuario,
                plantilla_id=plantilla_id
            )
            favorito.delete()
            
            return self.success_response(
                data=None,
                message="Plantilla removida de favoritos exitosamente",
                code="favorite_removed",
                http_status=200
            )
                
        except PlantillaFavorita.DoesNotExist:
            return self.error_response(
                errors="La plantilla no está en favoritos",
                message="Recurso no encontrado",
                code="not_found",
                http_status=404
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error interno del servidor",
                code="server_error",
                http_status=500
            )
    
    @action(detail=False, methods=['get'])
    def mis_favoritos(self, request):
        """Obtener plantillas favoritas del usuario"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    errors="Usuario no autenticado",
                    message="Autenticación requerida",
                    code="authentication_required",
                    http_status=401
                )
            
            usuario = request.user
            favoritos = PlantillaFavorita.objects.filter(usuario=usuario).select_related('plantilla')
            
            plantillas_favoritas = []
            for favorito in favoritos:
                plantilla = favorito.plantilla
                plantillas_favoritas.append({
                    'id': plantilla.id,
                    'nombre': plantilla.nombre,
                    'descripcion': plantilla.descripcion,
                    'fecha_creacion': plantilla.fecha_creacion,
                    'fecha_agregado_favorito': favorito.fecha_agregado,
                    'es_favorito': True
                })
            
            return self.success_response(
                data=plantillas_favoritas,
                message="Plantillas favoritas obtenidas exitosamente",
                code="favorites_retrieved",
                http_status=200
            )
                
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener favoritos",
                code="favorites_error",
                http_status=500
            )

class PlantillaCompartidaViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PlantillaCompartida.objects.none()
    serializer_class = PlantillaCompartidaSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PlantillaCompartida.objects.none()
        user = self.request.user
        return PlantillaCompartida.objects.filter(models.Q(usuario=user) | models.Q(plantilla__usuario=user)).distinct()

    def list(self, request, *args, **kwargs):
        """Listar plantillas compartidas con formato estándar"""
        return self.paginated_list_response(
            request=request,
            queryset=self.get_queryset(),
            serializer_class=self.serializer_class,
            paginated_message="Plantillas compartidas obtenidas exitosamente (paginadas)",
            unpaginated_message="Plantillas compartidas obtenidas exitosamente",
            code="shared_templates_retrieved",
            error_code="shared_templates_error"
        )

    def create(self, request, *args, **kwargs):
        """Crear plantilla compartida con formato estándar"""
        return self.standard_create_response(
            request=request,
            success_message="Plantilla compartida exitosamente",
            code="template_shared",
            error_message="Error al compartir plantilla",
            error_code="template_share_error"
        )

    def retrieve(self, request, *args, **kwargs):
        """Obtener plantilla compartida específica con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Plantilla compartida obtenida exitosamente",
                code="shared_template_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantilla compartida: {str(e)}",
                code="shared_template_retrieval_error"
            )

    def update(self, request, *args, **kwargs):
        """Actualizar plantilla compartida con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla compartida actualizada exitosamente",
                    code="shared_template_updated"
                )
            else:
                return self.error_response(
                    message="Datos inválidos para actualizar plantilla compartida",
                    code="shared_template_update_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar plantilla compartida: {str(e)}",
                code="shared_template_update_error"
            )

    def partial_update(self, request, *args, **kwargs):
        """Actualizar parcialmente plantilla compartida con formato estándar"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla compartida actualizada exitosamente",
                    code="shared_template_updated"
                )
            else:
                return self.error_response(
                    message="Datos inválidos para actualizar plantilla compartida",
                    code="shared_template_update_error",
                    errors=serializer.errors
                )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar plantilla compartida: {str(e)}",
                code="shared_template_update_error"
            )

    def destroy(self, request, *args, **kwargs):
        """Eliminar plantilla compartida con formato estándar"""
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                message="Plantilla compartida eliminada exitosamente",
                code="shared_template_deleted"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al eliminar plantilla compartida: {str(e)}",
                code="shared_template_deletion_error"
            )

    @action(detail=False, methods=['get'])
    def compartidas_conmigo(self, request):
        """Obtener plantillas compartidas conmigo con formato estándar"""
        try:
            user = request.user
            if not user or not user.is_authenticated:
                return self.error_response(
                    message="Usuario no autenticado",
                    code="authentication_required"
                )
            
            compartidas = PlantillaCompartida.objects.filter(usuario=user)
            serializer = self.get_serializer(compartidas, many=True)
            return self.success_response(
                data=serializer.data,
                message="Plantillas compartidas conmigo obtenidas exitosamente",
                code="shared_with_me_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantillas compartidas conmigo: {str(e)}",
                code="shared_with_me_error"
            )

    @action(detail=False, methods=['post'])
    def compartir(self, request):
        """Compartir una plantilla con uno o varios usuarios con formato estándar"""
        try:
            plantilla_id = request.data.get('plantilla_id')
            usuario_id = request.data.get('usuario_id')
            usuario_ids = request.data.get('usuario_ids')
            permisos = request.data.get('permisos', 'lectura')
            
            if not plantilla_id or (not usuario_id and not usuario_ids):
                return self.error_response(
                    message="plantilla_id y usuario_id(s) son requeridos",
                    code="missing_required_fields"
                )
            
            ids = []
            if usuario_ids:
                ids = usuario_ids if isinstance(usuario_ids, list) else [usuario_ids]
            elif usuario_id:
                ids = [usuario_id]
            
            compartidas = []
            for uid in ids:
                compartida, created = PlantillaCompartida.objects.get_or_create(
                    plantilla_id=plantilla_id,
                    usuario_id=uid,
                    defaults={'permisos': permisos}
                )
                if not created:
                    compartida.permisos = permisos
                    compartida.save()
                compartidas.append({'id': compartida.id, 'usuario_id': uid})
            
            return self.success_response(
                data={'compartidas': compartidas},
                message="Plantilla compartida correctamente",
                code="template_shared_successfully"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al compartir plantilla: {str(e)}",
                code="template_share_error"
            )

    @action(detail=True, methods=['delete'])
    def revocar(self, request, pk=None):
        """Revocar acceso a una plantilla compartida con formato estándar"""
        try:
            compartida = self.get_object()
            compartida.delete()
            return self.success_response(
                message="Acceso revocado exitosamente",
                code="access_revoked"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al revocar acceso: {str(e)}",
                code="access_revoke_error"
            )

    @action(detail=False, methods=['get'])
    def usuarios_compartidos(self, request):
        """Obtener usuarios con los que se ha compartido una plantilla con formato estándar"""
        try:
            plantilla_id = request.query_params.get('plantilla_id')
            if not plantilla_id:
                return self.error_response(
                    message="plantilla_id es requerido",
                    code="missing_plantilla_id"
                )
            
            compartidas = PlantillaCompartida.objects.filter(plantilla_id=plantilla_id)
            data = [
                {
                    'id': c.id,
                    'usuario': c.usuario.id,
                    'usuario_username': c.usuario.username,
                    'usuario_email': c.usuario.email,
                    'permisos': c.permisos,
                    'fecha_compartida': c.fecha_compartida,
                }
                for c in compartidas
            ]
            return self.success_response(
                data=data,
                message="Usuarios compartidos obtenidos exitosamente",
                code="shared_users_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener usuarios compartidos: {str(e)}",
                code="shared_users_error"
            )

class ClasificacionPlantillaGeneralViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = ClasificacionPlantillaGeneral.objects.all()
    serializer_class = ClasificacionPlantillaGeneralSerializer

    def list(self, request, *args, **kwargs):
        """Listar clasificaciones de plantilla general"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            return self.paginated_list_response(
                request,
                queryset,
                self.get_serializer_class(),
                paginated_message="Listado paginado de clasificaciones de plantilla general obtenido correctamente",
                unpaginated_message="Listado de clasificaciones de plantilla general obtenido correctamente",
                code="classification_list_retrieved",
                error_code="classification_list_error"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener las clasificaciones de plantilla general: {str(e)}",
                code="classification_list_error"
            )

    def create(self, request, *args, **kwargs):
        """Crear nueva clasificación de plantilla general"""
        try:
            return self.standard_create_response(
                request,
                self.get_serializer_class(),
                success_message="Clasificación de plantilla general creada correctamente",
                success_code="classification_created",
                error_message="Error al crear la clasificación de plantilla general",
                error_code="classification_creation_error"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al crear la clasificación de plantilla general: {str(e)}",
                code="classification_creation_error"
            )

    def retrieve(self, request, *args, **kwargs):
        """Obtener una clasificación de plantilla general específica"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Clasificación de plantilla general obtenida correctamente",
                code="classification_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener la clasificación de plantilla general: {str(e)}",
                code="classification_retrieval_error"
            )

    def update(self, request, *args, **kwargs):
        """Actualizar clasificación de plantilla general completa"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Clasificación de plantilla general actualizada correctamente",
                    code="classification_updated"
                )
            return self.error_response(
                message="Datos inválidos para actualizar la clasificación",
                code="classification_update_validation_error",
                data=serializer.errors
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar la clasificación de plantilla general: {str(e)}",
                code="classification_update_error"
            )

    def partial_update(self, request, *args, **kwargs):
        """Actualizar clasificación de plantilla general parcial"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Clasificación de plantilla general actualizada correctamente",
                    code="classification_updated"
                )
            return self.error_response(
                message="Datos inválidos para actualizar la clasificación",
                code="classification_update_validation_error",
                data=serializer.errors
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar la clasificación de plantilla general: {str(e)}",
                code="classification_update_error"
            )

    def destroy(self, request, *args, **kwargs):
        """Eliminar clasificación de plantilla general"""
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                message="Clasificación de plantilla general eliminada correctamente",
                code="classification_deleted"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al eliminar la clasificación de plantilla general: {str(e)}",
                code="classification_deletion_error"
            )

class PlantillaGeneralViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = PlantillaGeneral.objects.all()
    serializer_class = PlantillaGeneralSerializer

    def list(self, request, *args, **kwargs):
        """Listar plantillas generales"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            return self.paginated_list_response(
                request,
                queryset,
                self.get_serializer_class(),
                paginated_message="Listado paginado de plantillas generales obtenido correctamente",
                unpaginated_message="Listado de plantillas generales obtenido correctamente",
                code="general_templates_retrieved",
                error_code="general_templates_list_error"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener las plantillas generales: {str(e)}",
                code="general_templates_list_error"
            )

    def create(self, request, *args, **kwargs):
        """Crear nueva plantilla general"""
        try:
            return self.standard_create_response(
                request,
                self.get_serializer_class(),
                success_message="Plantilla general creada correctamente",
                success_code="general_template_created",
                error_message="Error al crear la plantilla general",
                error_code="general_template_creation_error"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al crear la plantilla general: {str(e)}",
                code="general_template_creation_error"
            )

    def retrieve(self, request, *args, **kwargs):
        """Obtener una plantilla general específica"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Plantilla general obtenida correctamente",
                code="general_template_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener la plantilla general: {str(e)}",
                code="general_template_retrieval_error"
            )

    def update(self, request, *args, **kwargs):
        """Actualizar plantilla general completa"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla general actualizada correctamente",
                    code="general_template_updated"
                )
            return self.error_response(
                message="Datos inválidos para actualizar la plantilla",
                code="general_template_update_validation_error",
                data=serializer.errors
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar la plantilla general: {str(e)}",
                code="general_template_update_error"
            )

    def partial_update(self, request, *args, **kwargs):
        """Actualizar plantilla general parcial"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.success_response(
                    data=serializer.data,
                    message="Plantilla general actualizada correctamente",
                    code="general_template_updated"
                )
            return self.error_response(
                message="Datos inválidos para actualizar la plantilla",
                code="general_template_update_validation_error",
                data=serializer.errors
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al actualizar la plantilla general: {str(e)}",
                code="general_template_update_error"
            )

    def destroy(self, request, *args, **kwargs):
        """Eliminar plantilla general"""
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                message="Plantilla general eliminada correctamente",
                code="general_template_deleted"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al eliminar la plantilla general: {str(e)}",
                code="general_template_deletion_error"
            )

    @action(detail=True, methods=['get'])
    def plantillas_por_clasificacion(self, request, pk=None):
        """Obtener plantillas agrupadas por clasificación"""
        try:
            plantilla_general = self.get_object()
            data = plantilla_general.get_plantillas_por_clasificacion()
            return self.success_response(
                data=data,
                message="Plantillas por clasificación obtenidas correctamente",
                code="templates_by_classification_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantillas por clasificación: {str(e)}",
                code="templates_by_classification_error"
            )

    @action(detail=True, methods=['post'])
    def compartir(self, request, pk=None):
        """Compartir plantilla general con usuarios específicos"""
        try:
            plantilla_general = self.get_object()
            usuarios_ids = request.data.get('usuarios_ids', [])
            fecha_vencimiento = request.data.get('fecha_vencimiento')
            
            if not usuarios_ids:
                return self.error_response(
                    message="Debe especificar al menos un usuario",
                    code="no_users_specified"
                )
            
            # Crear registros de compartición
            compartidas_creadas = []
            for usuario_id in usuarios_ids:
                try:
                    usuario = User.objects.get(id=usuario_id)
                    compartida, created = PlantillaGeneralCompartida.objects.get_or_create(
                        plantilla_general=plantilla_general,
                        usuario_asignado=usuario,
                        defaults={
                            'usuario_que_comparte': request.user,
                            'fecha_vencimiento': fecha_vencimiento
                        }
                    )
                    if created:
                        compartidas_creadas.append(compartida)
                except Usuario.DoesNotExist:
                    continue
            
            return self.success_response(
                data={
                    'compartidas_creadas': len(compartidas_creadas),
                    'total_usuarios': len(usuarios_ids)
                },
                message=f"Plantilla compartida con {len(compartidas_creadas)} usuarios",
                code="template_shared"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al compartir plantilla: {str(e)}",
                code="template_sharing_error"
            )

    @action(detail=True, methods=['get'])
    def usuarios_con_acceso(self, request, pk=None):
        """Obtener usuarios que tienen acceso a esta plantilla general"""
        try:
            plantilla_general = self.get_object()
            compartidas = PlantillaGeneralCompartida.objects.filter(
                plantilla_general=plantilla_general
            ).select_related('usuario', 'asignado_por')
            
            usuarios_data = []
            for compartida in compartidas:
                usuarios_data.append({
                    'id': compartida.usuario.id,
                    'username': compartida.usuario.username,
                    'email': compartida.usuario.email,
                    'fecha_asignacion': compartida.fecha_asignacion,
                    'fecha_expiracion': compartida.fecha_expiracion,
                    'esta_vigente': compartida.esta_vigente(),
                    'asignado_por': compartida.asignado_por.username
                })
            
            return self.success_response(
                data=usuarios_data,
                message="Usuarios con acceso obtenidos correctamente",
                code="users_with_access_retrieved"
            )
        except Exception as e:
            return self.error_response(
                 message=f"Error al obtener usuarios con acceso: {str(e)}",
                 code="users_with_access_error"
             )


class PlantillaGeneralCompartidaViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar plantillas generales compartidas"""
    queryset = PlantillaGeneralCompartida.objects.all()
    serializer_class = PlantillaGeneralCompartidaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['plantilla_general__nombre', 'usuario__username', 'asignado_por__username']
    ordering_fields = ['fecha_asignacion', 'fecha_expiracion']
    ordering = ['-fecha_asignacion']

    def get_queryset(self):
        """Filtrar plantillas compartidas según el usuario"""
        user = self.request.user
        if not user.is_authenticated:
            return PlantillaGeneralCompartida.objects.none()
        
        if user.is_staff:
            # Los administradores pueden ver todas las plantillas compartidas
            return PlantillaGeneralCompartida.objects.all().select_related(
                'plantilla_general', 'usuario', 'asignado_por'
            )
        else:
            # Los usuarios solo pueden ver las plantillas compartidas con ellos
            return PlantillaGeneralCompartida.objects.filter(
                usuario=user
            ).select_related(
                'plantilla_general', 'usuario', 'asignado_por'
            )

    @action(detail=False, methods=['get'])
    def mis_plantillas_compartidas(self, request):
        """Obtener plantillas compartidas con el usuario actual"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    message="Usuario no autenticado",
                    code="authentication_required",
                    http_status=401
                )
            
            compartidas = self.get_queryset().filter(usuario=request.user)
            serializer = self.get_serializer(compartidas, many=True)
            return self.success_response(
                data=serializer.data,
                message="Plantillas compartidas obtenidas correctamente",
                code="shared_templates_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantillas compartidas: {str(e)}",
                code="shared_templates_error"
            )

    @action(detail=False, methods=['get'])
    def plantillas_vigentes(self, request):
        """Obtener solo las plantillas compartidas vigentes"""
        try:
            if not request.user.is_authenticated:
                return self.error_response(
                    message="Usuario no autenticado",
                    code="authentication_required",
                    http_status=401
                )
            
            compartidas = self.get_queryset().filter(usuario=request.user)
            vigentes = [c for c in compartidas if c.esta_vigente()]
            serializer = self.get_serializer(vigentes, many=True)
            return self.success_response(
                data=serializer.data,
                message="Plantillas vigentes obtenidas correctamente",
                code="valid_shared_templates_retrieved"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al obtener plantillas vigentes: {str(e)}",
                code="valid_shared_templates_error"
            )

    @action(detail=True, methods=['delete'])
    def revocar_acceso(self, request, pk=None):
        """Revocar acceso a una plantilla compartida"""
        try:
            compartida = self.get_object()
            # Solo el usuario que asignó o un admin puede revocar el acceso
            if request.user != compartida.asignado_por and not request.user.is_staff:
                return self.error_response(
                    message="No tiene permisos para revocar este acceso",
                    code="permission_denied"
                )
            
            compartida.delete()
            return self.success_response(
                message="Acceso revocado correctamente",
                code="access_revoked"
            )
        except Exception as e:
            return self.error_response(
                message=f"Error al revocar acceso: {str(e)}",
                code="revoke_access_error"
            )


class ConvertDocxToHtmlView(StandardResponseMixin, APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            if not uploaded_file.name.endswith('.docx'):
                return self.error_response("Solo se permiten archivos .docx")
            try:
                # Read the uploaded file
                doc = docx.Document(uploaded_file.file)
                html = ""
                in_list = False
                for block in iter_block_items(doc):
                    if isinstance(block, Table):
                        html += "<table border='1' style='border-collapse:collapse;margin:10px 0;'>"
                        for row in block.rows:
                            html += "<tr>"
                            for cell in row.cells:
                                html += f"<td>{cell.text}</td>"
                            html += "</tr>"
                        html += "</table>"
                    elif isinstance(block, docx.text.paragraph.Paragraph):
                        p = block
                        style = p.style.name.lower()
                        text = p.text.replace(" ", "&nbsp;")
                        align = ""
                        if p.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                            align = "text-align:center;"
                        elif p.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
                            align = "text-align:right;"
                        elif p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                            align = "text-align:justify;"
                        indent = ""
                        if p.paragraph_format.first_line_indent:
                            indent += f"text-indent:{int(p.paragraph_format.first_line_indent.pt)}pt;"
                        if p.paragraph_format.left_indent:
                            indent += f"margin-left:{int(p.paragraph_format.left_indent.pt)}pt;"
                        style_attr = f'style="{align}{indent}"' if (align or indent) else ""
                        # Detectar listas
                        if is_list_paragraph(p):
                            if not in_list:
                                html += "<ul>"
                                in_list = True
                            html += f"<li {style_attr}>{text}</li>"
                        else:
                            if in_list:
                                html += "</ul>"
                                in_list = False
                            if style.startswith("heading"):
                                html += f"<h2 {style_attr}>{text}</h2>"
                            else:
                                html += f"<p {style_attr}>{text}</p>"
                if in_list:
                    html += "</ul>"
                html += ""
                return self.success_response(data=html, message="Operación realizada con éxito", code="success", http_status=200)
            except Exception as e:
                return self.error_response(f"Error en la conversión: {str(e)}")
        else:
            return self.error_response(serializer.errors)

class ConvertImageToHtmlView(StandardResponseMixin, APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            if not uploaded_file.name.endswith('.png'):
                return self.error_response("Solo se permiten archivos .png")
            try:
                # Read the uploaded file
                image_bytes = uploaded_file.read()
                img = Image.open(io.BytesIO(image_bytes))

                # Usar pytesseract para obtener datos de cada palabra
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                n = len(ocr_data['level'])
                lines = {}
                for i in range(n):
                    if int(ocr_data['conf'][i]) > 0 and ocr_data['text'][i].strip():
                        # Agrupar por número de línea y número de bloque para mayor fidelidad
                        block_num = ocr_data['block_num'][i]
                        par_num = ocr_data['par_num'][i]
                        line_num = ocr_data['line_num'][i]
                        key = (block_num, par_num, line_num)
                        if key not in lines:
                            lines[key] = []
                        lines[key].append({
                            'text': ocr_data['text'][i],
                            'left': ocr_data['left'][i],
                            'top': ocr_data['top'][i],
                            'width': ocr_data['width'][i]
                        })
                html = ""
                for key in sorted(lines.keys(), key=lambda k: (k[0], k[1], k[2])):
                    line = lines[key]
                    if not line:
                        continue
                    # Ordenar palabras por posición horizontal
                    line.sort(key=lambda w: w['left'])
                    # Espacios desde el margen izquierdo hasta la primera palabra
                    first_word = line[0]
                    n_spaces = int(first_word['left'] // 10)  # Ajusta el divisor según el resultado visual
                    line_text = " " * n_spaces
                    prev_right = first_word['left'] + first_word['width']
                    line_text += first_word['text']
                    for word in line[1:]:
                        # Calcular espacios entre palabras según la distancia X
                        gap = word['left'] - prev_right
                        if gap > 10:
                            spaces_between = int(gap // 10)
                            line_text += " " * max(1, spaces_between)
                        else:
                            line_text += " "
                        line_text += word['text']
                        prev_right = word['left'] + word['width']
                    html += line_text + "\n"
                return self.success_response(data=html, message="Operación realizada con éxito", code="success", http_status=200)
            except Exception as e:
                return self.error_response(f"Error en la conversión: {str(e)}")
        else:
            return self.error_response(serializer.errors)

class ConvertPdfToHtmlView(StandardResponseMixin, APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            if not uploaded_file.name.endswith('.pdf'):
                return self.error_response("Solo se permiten archivos .pdf")
            try:
                # Read the uploaded file
                pdf_bytes = uploaded_file.read()
                pdf_buffer = io.BytesIO(pdf_bytes)
                pdf = pdfplumber.open(pdf_buffer)
                html = ""
                for page in pdf.pages:
                    words = page.extract_words()
                    # Agrupa palabras por línea (top)
                    lines = {}
                    for word in words:
                        line_key = round(word['top'])
                        if line_key not in lines:
                            lines[line_key] = []
                        lines[line_key].append(word)
                    for line_words in lines.values():
                        line_words.sort(key=lambda w: w['x0'])
                        prev_x1 = None
                        line = ""
                        for idx, word in enumerate(line_words):
                            if idx == 0:
                                # Primera palabra de la línea
                                n_dollars = int(word['x0'] // 5)  # Ajusta el divisor según el resultado visual
                                line += "&nbsp;" * n_dollars
                            else:
                                gap = word['x0'] - prev_x1
                                if gap > 5:
                                    n_spaces = int(gap // 3)
                                    line += " " * max(1, n_spaces)
                                else:
                                    line += " "
                            line += word['text']
                            prev_x1 = word['x1']
                        html += line + "\n"
                return self.success_response(data=html, message="Operación realizada con éxito", code="success", http_status=200)
            except Exception as e:
                return self.error_response(f"Error en la conversión: {str(e)}")
        else:
            return self.error_response(serializer.errors)

def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def is_list_paragraph(paragraph):
    # Detecta si el párrafo es una lista por el estilo o por el XML
    style = paragraph.style.name.lower()
    if "list" in style or "bullet" in style:
        return True
    # XML: busca el elemento numPr
    if paragraph._element.xpath('.//w:numPr'):
        return True
    return False

class UsuariosViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """ViewSet para listar usuarios (excluyendo al usuario actual)"""
    queryset = Usuarios.objects.none()
    serializer_class = UsuariosSerializer
    
    def get_queryset(self):
        """Obtener todos los usuarios excepto el usuario actual"""
        if self.request.user.is_authenticated:
            return Usuarios.objects.exclude(id=self.request.user.id)
        return Usuarios.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Listar usuarios con formato estándar"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Usuarios obtenidos exitosamente",
                code="users_retrieved",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener usuarios",
                code="users_error",
                http_status=500
            )