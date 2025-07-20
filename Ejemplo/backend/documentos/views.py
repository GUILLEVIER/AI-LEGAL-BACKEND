import os
import io
import json
import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pdfplumber
from PIL import Image
import pytesseract
import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.table import Table
from docx.text.paragraph import Paragraph
from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    DocumentoSubido, 
    CampoDisponible, 
    PlantillaDocumento, 
    CampoPlantilla, 
    DocumentoGenerado,
    FavoritoPlantilla,
    TipoPlantillaDocumento,
    PlantillaCompartida
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
    FavoritoPlantillaSerializer,
)

# Configuración automática de TESSDATA_PREFIX para Tesseract
"""if 'TESSDATA_PREFIX' not in os.environ:
    # Rutas comunes en Mac y Linux
    posibles_rutas = [
        '/opt/homebrew/share/tessdata/',
        '/usr/share/tesseract-ocr/4.00/tessdata/',
        '/usr/share/tesseract-ocr/tessdata/',
        '/usr/share/tessdata/',
    ]
    for ruta in posibles_rutas:
        if os.path.exists(os.path.join(ruta, 'spa.traineddata')):
            os.environ['TESSDATA_PREFIX'] = ruta
            break
"""
class DocumentoSubidoViewSet(viewsets.ModelViewSet):
    queryset = DocumentoSubido.objects.all()
    serializer_class = DocumentoSubidoSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'])
    def subir_documento(self, request):
        """Subir documento y extraer texto"""
        try:
            archivo = request.FILES.get('archivo')
            if not archivo:
                return Response({'error': 'No se proporcionó archivo'}, status=400)

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

            # Crear registro en base de datos
            documento = DocumentoSubido.objects.create(
                usuario=request.user if request.user.is_authenticated else User.objects.first(),
                nombre_original=archivo.name,
                tipo=tipo,
                archivo_url=ruta_completa
            )

            return Response({
                'id': documento.id,
                'texto_extraido': texto_extraido,
                'tipo': tipo,
                'nombre_original': archivo.name
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)

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

class CampoDisponibleViewSet(viewsets.ModelViewSet):
    queryset = CampoDisponible.objects.all()
    serializer_class = CampoDisponibleSerializer

class TipoPlantillaDocumentoViewSet(viewsets.ModelViewSet):
    queryset = TipoPlantillaDocumento.objects.all()
    serializer_class = TipoPlantillaDocumentoSerializer

class PlantillaDocumentoViewSet(viewsets.ModelViewSet):
    queryset = PlantillaDocumento.objects.none()
    serializer_class = PlantillaDocumentoSerializer

    def get_queryset(self):
        user = self.request.user
        # Plantillas propias o compartidas conmigo
        compartidas_ids = PlantillaCompartida.objects.filter(usuario=user).values_list('plantilla_id', flat=True)
        return PlantillaDocumento.objects.filter(
            models.Q(usuario=user) | models.Q(id__in=compartidas_ids)
        ).distinct()
    
    def list(self, request, *args, **kwargs):
        print("list")
        """Listar plantillas con información de favoritos"""
        try:
            usuario = request.user if request.user.is_authenticated else User.objects.first()
            plantillas = self.get_queryset()  # Solo las del usuario
            
            # Obtener favoritos del usuario
            favoritos_usuario = FavoritoPlantilla.objects.filter(usuario=usuario).values_list('plantilla_id', flat=True)
            
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
            
            return Response(plantillas_con_favoritos, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def crear_plantilla(self, request):
        print("=== CREAR PLANTILLA ===")
        print("Request data:", request.data)
        print("Request method:", request.method)
        print("Request data:", request.data)
        """Crear plantilla con campos asociados"""
        serializer = CrearPlantillaSerializer(data=request.data)
        print("Serializer is valid:", serializer.is_valid())
        print("Serializer validated data:", serializer.validated_data if serializer.is_valid() else "Invalid")
        if serializer.is_valid():
            try:
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

                # Crear plantilla
                plantilla = PlantillaDocumento.objects.create(
                    nombre=serializer.validated_data['nombre'],
                    descripcion=serializer.validated_data.get('descripcion', ''),
                    html_con_campos=serializer.validated_data.get('html_con_campos', ''),
                    tipo=tipo,
                    usuario=request.user if request.user.is_authenticated else User.objects.first()
                )

                # Crear campos asociados
                campos = serializer.validated_data.get('campos', [])
                for campo_data in campos:
                    CampoPlantilla.objects.create(
                        plantilla=plantilla,
                        campo_id=campo_data['campo_id'],
                        nombre_variable=campo_data['nombre_variable']
                    )

                return Response({
                    'id': plantilla.id,
                    'mensaje': 'Plantilla creada exitosamente'
                })

            except Exception as e:
                return Response({'error': str(e)}, status=500)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=400)

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

                # Crear documento generado
                documento = DocumentoGenerado.objects.create(
                    plantilla=plantilla,
                    datos_rellenados=datos,
                    html_resultante=html_resultante
                )

                return Response({
                    'id': documento.id,
                    'html_resultante': html_resultante,
                    'mensaje': 'Documento generado exitosamente'
                })

            else:
                return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def partial_update(self, request, *args, **kwargs):
        print("partial_update")
        print(request)
        print(request.data)
        instance = self.get_object()
        data = request.data

        # Quitar campo asociado (flujo rápido)
        if 'quitar_campo_id' in data:
            campo_plantilla_id = data['quitar_campo_id']
            from .models import CampoPlantilla
            print(f"[LOG] Quitar campo asociado: {campo_plantilla_id}")
            CampoPlantilla.objects.filter(id=campo_plantilla_id, plantilla=instance).delete()
            return Response({'mensaje': 'Campo asociado eliminado'}, status=status.HTTP_200_OK)

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
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        print("destroy")
        instance = self.get_object()
        print(f"[LOG] Eliminando plantilla: {instance.id} - {instance.nombre}")
        return super().destroy(request, *args, **kwargs)

class DocumentoGeneradoViewSet(viewsets.ModelViewSet):
    queryset = DocumentoGenerado.objects.none()
    serializer_class = DocumentoGeneradoSerializer

    def get_queryset(self):
        user = self.request.user
        return DocumentoGenerado.objects.filter(plantilla__usuario=user)

class FavoritoPlantillaViewSet(viewsets.ModelViewSet):
    queryset = FavoritoPlantilla.objects.none()
    serializer_class = FavoritoPlantillaSerializer

    def get_queryset(self):
        user = self.request.user
        return FavoritoPlantilla.objects.filter(usuario=user)
    
    @action(detail=False, methods=['post'])
    def agregar_favorito(self, request):
        """Agregar plantilla a favoritos"""
        try:
            plantilla_id = request.data.get('plantilla_id')
            if not plantilla_id:
                return Response({'error': 'plantilla_id es requerido'}, status=400)
            
            plantilla = PlantillaDocumento.objects.get(id=plantilla_id)
            usuario = request.user if request.user.is_authenticated else User.objects.first()
            
            # Verificar si ya existe
            favorito, created = FavoritoPlantilla.objects.get_or_create(
                usuario=usuario,
                plantilla=plantilla
            )
            
            if created:
                return Response({'message': 'Plantilla agregada a favoritos'}, status=201)
            else:
                return Response({'message': 'La plantilla ya está en favoritos'}, status=200)
                
        except PlantillaDocumento.DoesNotExist:
            return Response({'error': 'Plantilla no encontrada'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['delete'])
    def quitar_favorito(self, request):
        """Quitar plantilla de favoritos"""
        try:
            plantilla_id = request.data.get('plantilla_id')
            if not plantilla_id:
                return Response({'error': 'plantilla_id es requerido'}, status=400)
            
            usuario = request.user if request.user.is_authenticated else User.objects.first()
            
            favorito = FavoritoPlantilla.objects.get(
                usuario=usuario,
                plantilla_id=plantilla_id
            )
            favorito.delete()
            
            return Response({'message': 'Plantilla removida de favoritos'}, status=200)
                
        except FavoritoPlantilla.DoesNotExist:
            return Response({'error': 'La plantilla no está en favoritos'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def mis_favoritos(self, request):
        """Obtener plantillas favoritas del usuario"""
        try:
            usuario = request.user if request.user.is_authenticated else User.objects.first()
            favoritos = FavoritoPlantilla.objects.filter(usuario=usuario).select_related('plantilla')
            
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
            
            return Response(plantillas_favoritas, status=200)
                
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class PlantillaCompartidaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PlantillaCompartida.objects.none()
    serializer_class = PlantillaCompartidaSerializer

    def get_queryset(self):
        user = self.request.user
        return PlantillaCompartida.objects.filter(models.Q(usuario=user) | models.Q(plantilla__usuario=user)).distinct()

    @action(detail=False, methods=['get'])
    def compartidas_conmigo(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'error': 'No autenticado'}, status=401)
        compartidas = PlantillaCompartida.objects.filter(usuario=user)
        serializer = self.get_serializer(compartidas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def compartir(self, request):
        """Compartir una plantilla con uno o varios usuarios"""
        plantilla_id = request.data.get('plantilla_id')
        usuario_id = request.data.get('usuario_id')
        usuario_ids = request.data.get('usuario_ids')
        permisos = request.data.get('permisos', 'lectura')
        if not plantilla_id or (not usuario_id and not usuario_ids):
            return Response({'error': 'plantilla_id y usuario_id(s) son requeridos'}, status=400)
        try:
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
            return Response({'message': 'Plantilla compartida correctamente', 'compartidas': compartidas})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['delete'])
    def revocar(self, request, pk=None):
        """Revocar acceso a una plantilla compartida"""
        try:
            compartida = self.get_object()
            compartida.delete()
            return Response({'message': 'Acceso revocado'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def usuarios_compartidos(self, request):
        plantilla_id = request.query_params.get('plantilla_id')
        if not plantilla_id:
            return Response({'error': 'plantilla_id es requerido'}, status=400)
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
        return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_usuarios(request):
    usuarios = User.objects.exclude(id=request.user.id)
    data = [{'id': u.id, 'username': u.username, 'email': u.email} for u in usuarios]
    print("data: ", data)
    return Response(data)
