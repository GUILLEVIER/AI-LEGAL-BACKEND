import html
import io

import fitz
import pymupdf
import pytesseract
from PIL import Image
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status

import mammoth

from .models import (
    TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos,
    Clasificacion, Plantillas
)
from .serializers import (
    TipoDocumentoSerializer, DocumentosSerializer, FavoritosSerializer, CompartirSerializer,
    EscritosSerializer, DemandasSerializer, ContratosSerializer, ClasificacionSerializer,
    PlantillasSerializer
)

class TipoDocumentoListAPIView(generics.ListCreateAPIView):
    queryset = TipoDocumento.objects.all() # type: ignore
    serializer_class = TipoDocumentoSerializer

class DocumentosListAPIView(generics.ListCreateAPIView):
    serializer_class = DocumentosSerializer

    def get_queryset(self):
        usuario = self.request.user
        return (
            Documentos.objects # type: ignore
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
            Favoritos.objects # type: ignore
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
            Compartir.objects # type: ignore
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
            Escritos.objects # type: ignore
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
            Demandas.objects # type: ignore
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
            Contratos.objects # type: ignore
            .select_related('documento', 'tribunales', 'created_by')
            .filter(created_by__empresa=usuario.empresa)
        )

    def perform_create(self, serializer):
        usuario = self.request.user
        serializer.save(created_by=usuario)

class ClasificacionListAPIView(generics.ListCreateAPIView):
    queryset = Clasificacion.objects.all() # type: ignore
    serializer_class = ClasificacionSerializer

class PlantillasListAPIView(generics.ListCreateAPIView):
    queryset = Plantillas.objects.all() # type: ignore
    serializer_class = PlantillasSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser])
def convert_docx_to_html(request):
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_file = request.FILES['file']
    
    # Check if file is a DOCX
    if not uploaded_file.name.endswith('.docx'):
        return Response(
            {'error': 'Only .docx files are allowed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Read the uploaded file
        docx_content = uploaded_file.read()
        docx_file_object = io.BytesIO(docx_content)
        
        # Convert DOCX to HTML using mammoth
        result = mammoth.convert_to_html(docx_file_object)
        html_content = result.value
        messages = result.messages  # Optional: for warnings/errors during conversion
        
        return HttpResponse({
            html_content,
        }, status=status.HTTP_200_OK)

        """return Response({
            'html': html_content,
            'messages': messages
        }, status=status.HTTP_200_OK)"""
        
    except Exception as e:
        return Response(
            {'error': f'Conversion failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([MultiPartParser])
def convert_image_to_text(request):
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    uploaded_file = request.FILES['file']

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

        # Perform OCR
        extracted_text = pytesseract.image_to_string(img)
        print(extracted_text)

        return HttpResponse({
            extracted_text
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Conversion failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@parser_classes([MultiPartParser])
def convert_pdf_to_html(request):
    if 'file' not in request.FILES:
        print(request.FILES)
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    uploaded_file = request.FILES['file']

    # Check if file is a PDF
    if not uploaded_file.name.endswith('.pdf'):
        return Response(
            {'error': 'Only .pdf files are allowed'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Read the uploaded file
        pdf_bytes = uploaded_file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        html_content = ""

        # Iterate through the pages
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            print("page", page)
            # Get text content - using the correct PyMuPDF method
            html_content += page.get_text("html")
        print(html_content)
        pdf_document.close()
        return HttpResponse({
            html_content
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Conversion failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )