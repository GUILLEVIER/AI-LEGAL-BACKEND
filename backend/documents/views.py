import io
import pdfplumber
import pytesseract
from PIL import Image
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status

import docx
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

from .models import (
    TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos,
    Clasificacion, Plantillas
)
from .serializers import (
    TipoDocumentoSerializer, DocumentosSerializer, FavoritosSerializer, CompartirSerializer,
    EscritosSerializer, DemandasSerializer, ContratosSerializer, ClasificacionSerializer,
    PlantillasSerializer, FileUploadSerializer
)


class TipoDocumentoListAPIView(generics.ListCreateAPIView):
    queryset = TipoDocumento.objects.all()  # type: ignore
    serializer_class = TipoDocumentoSerializer


class DocumentosListAPIView(generics.ListCreateAPIView):
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


class FavoritosListAPIView(generics.ListCreateAPIView):
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


class CompartirListAPIView(generics.ListCreateAPIView):
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


class EscritosListAPIView(generics.ListCreateAPIView):
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


class DemandasListAPIView(generics.ListCreateAPIView):
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


class ContratosListAPIView(generics.ListCreateAPIView):
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


class ClasificacionListAPIView(generics.ListCreateAPIView):
    queryset = Clasificacion.objects.all()  # type: ignore
    serializer_class = ClasificacionSerializer


class PlantillasListAPIView(generics.ListCreateAPIView):
    queryset = Plantillas.objects.all()  # type: ignore
    serializer_class = PlantillasSerializer


def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield docx.text.paragraph.Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield docx.table.Table(child, parent)


def is_list_paragraph(paragraph):
    # Detecta si el párrafo es una lista por el estilo o por el XML
    style = paragraph.style.name.lower()
    if "list" in style or "bullet" in style:
        return True
    # XML: busca el elemento numPr
    if paragraph._element.xpath('.//w:numPr'):
        return True
    return False


@api_view(['POST'])
@parser_classes([MultiPartParser])
def convert_docx_to_html(request):
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        # Check if file is a DOCX
        if not uploaded_file.name.endswith('.docx'):
            return Response(
                {'error': 'Only .docx files are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Read the uploaded file
            doc = docx.Document(uploaded_file.file)
            html = ""
            in_list = False
            for block in iter_block_items(doc):
                if isinstance(block, docx.table.Table):
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
                    if p.alignment == docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER:
                        align = "text-align:center;"
                    elif p.alignment == docx.enum.text.WD_ALIGN_PARAGRAPH.RIGHT:
                        align = "text-align:right;"
                    elif p.alignment == docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY:
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
            return HttpResponse({
                f"<pre>\n{html}\n</pre>"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Conversion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([MultiPartParser])
def convert_image_to_html(request):
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        # Check if file is a PNG
        if not uploaded_file.name.endswith('.png'):
            return Response(
                {'error': 'Only .png files are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
            result = ""
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
                result += line_text + "\n"
            return HttpResponse({
                f"<pre>\n{result}</pre>"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Conversion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes([MultiPartParser])
def convert_pdf_to_html(request):
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.validated_data['file']
        # Check if file is a PDF
        if not uploaded_file.name.endswith('.pdf'):
            return Response(
                {'error': 'Only .pdf files are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Read the uploaded file
            pdf_bytes = uploaded_file.read()
            pdf_buffer = io.BytesIO(pdf_bytes)
            pdf = pdfplumber.open(pdf_buffer)
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
                    result += line + "\n"
            return HttpResponse({
                f"<pre>\n{result}</pre>"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Conversion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
