import io
import pdfplumber
import pytesseract
from PIL import Image
from rest_framework import generics
from rest_framework.parsers import MultiPartParser

import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.table import Table
from docx.text.paragraph import Paragraph
from rest_framework.views import APIView

from core.mixins import StandardResponseMixin

from .models import (
    TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos,
    Clasificacion, Plantillas
)
from .serializers import (
    TipoDocumentoSerializer, DocumentosSerializer, FavoritosSerializer, CompartirSerializer,
    EscritosSerializer, DemandasSerializer, ContratosSerializer, ClasificacionSerializer,
    PlantillasSerializer, FileUploadSerializer
)


class TipoDocumentoListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = TipoDocumento.objects.all()  # type: ignore
    serializer_class = TipoDocumentoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de tipos de documento",
            unpaginated_message="Listado de tipos de documento obtenido correctamente",
            code="tipo_documento_list",
            error_code="tipo_documento_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Tipo de documento creado exitosamente",
            code="tipo_documento_created",
            error_message="Error al crear el tipo de documento",
            error_code="tipo_documento_create_error",
            http_status=201,
            **kwargs
        )


class DocumentosListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = DocumentosSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Documentos.objects  # type: ignore
            .select_related('tipoDocumento', 'created_by', 'updated_by')
            .filter(created_by__empresa=usuario.empresa)
        )
    
    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(created_by=usuario)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de documentos",
            unpaginated_message="Listado de documentos obtenido correctamente",
            code="documentos_list",
            error_code="documentos_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Documento creado exitosamente",
            code="documento_created",
            error_message="Error al crear el documento",
            error_code="documento_create_error",
            http_status=201,
            **kwargs
        )


class FavoritosListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = FavoritosSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Favoritos.objects  # type: ignore
            .select_related('usuario', 'documento')
            .filter(usuario__empresa=usuario.empresa)
        )

    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(usuario=usuario)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de favoritos",
            unpaginated_message="Listado de favoritos obtenido correctamente",
            code="favoritos_list",
            error_code="favoritos_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Favorito agregado exitosamente",
            code="favorito_created",
            error_message="Error al agregar el favorito",
            error_code="favorito_create_error",
            http_status=201,
            **kwargs
        )


class CompartirListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = CompartirSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Compartir.objects  # type: ignore
            .select_related('usuario', 'documento')
            .prefetch_related('usuarios', 'empresas')
            .filter(usuario__empresa=usuario.empresa)
        )
    
    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(usuario=usuario)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de compartidos",
            unpaginated_message="Listado de compartidos obtenido correctamente",
            code="compartir_list",
            error_code="compartir_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Documento compartido exitosamente",
            code="compartir_created",
            error_message="Error al compartir el documento",
            error_code="compartir_create_error",
            http_status=201,
            **kwargs
        )


class EscritosListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = EscritosSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Escritos.objects  # type: ignore
            .select_related('documento', 'tribunales', 'created_by')
            .filter(created_by__empresa=usuario.empresa)
        )
        
    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(created_by=usuario)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de escritos",
            unpaginated_message="Listado de escritos obtenido correctamente",
            code="escritos_list",
            error_code="escritos_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Escrito creado exitosamente",
            code="escrito_created",
            error_message="Error al crear el escrito",
            error_code="escrito_create_error",
            http_status=201,
            **kwargs
        )


class DemandasListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = DemandasSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Demandas.objects  # type: ignore
            .select_related('documento', 'tribunales', 'created_by')
            .filter(created_by__empresa=usuario.empresa)
        )
        
    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(created_by=usuario)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de demandas",
            unpaginated_message="Listado de demandas obtenido correctamente",
            code="demandas_list",
            error_code="demandas_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Demanda creada exitosamente",
            code="demanda_created",
            error_message="Error al crear la demanda",
            error_code="demanda_create_error",
            http_status=201,
            **kwargs
        )


class ContratosListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    serializer_class = ContratosSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Contratos.objects  # type: ignore
            .select_related('documento', 'tribunales', 'created_by')
            .filter(created_by__empresa=usuario.empresa)
        )
        
    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(created_by=usuario)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de contratos",
            unpaginated_message="Listado de contratos obtenido correctamente",
            code="contratos_list",
            error_code="contratos_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Contrato creado exitosamente",
            code="contrato_created",
            error_message="Error al crear el contrato",
            error_code="contrato_create_error",
            http_status=201,
            **kwargs
        )


class ClasificacionListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Clasificacion.objects.all()  # type: ignore
    serializer_class = ClasificacionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de clasificaciones",
            unpaginated_message="Listado de clasificaciones obtenido correctamente",
            code="clasificacion_list",
            error_code="clasificacion_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Clasificación creada exitosamente",
            code="clasificacion_created",
            error_message="Error al crear la clasificación",
            error_code="clasificacion_create_error",
            http_status=201,
            **kwargs
        )


class PlantillasListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Plantillas.objects.all()  # type: ignore
    serializer_class = PlantillasSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de plantillas",
            unpaginated_message="Listado de plantillas obtenido correctamente",
            code="plantillas_list",
            error_code="plantillas_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Plantilla creada exitosamente",
            code="plantilla_created",
            error_message="Error al crear la plantilla",
            error_code="plantilla_create_error",
            http_status=201,
            **kwargs
        )


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
