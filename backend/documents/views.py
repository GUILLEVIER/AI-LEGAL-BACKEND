from rest_framework import generics
from .models import (
    TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos,
    Clasificacion, Plantillas, Tribunales
)
from .serializers import (
    TipoDocumentoSerializer, DocumentosSerializer, FavoritosSerializer, CompartirSerializer,
    EscritosSerializer, DemandasSerializer, ContratosSerializer, ClasificacionSerializer, PlantillasSerializer,
    TribunalesSerializer
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

class TribunalesListAPIView(generics.ListCreateAPIView):
    queryset = Tribunales.objects.all() # type: ignore
    serializer_class = TribunalesSerializer