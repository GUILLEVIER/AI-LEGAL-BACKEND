from rest_framework import generics
from .models import Empresas, Planes
from .serializers import EmpresasSerializer, PlanesSerializer

class EmpresasListAPIView(generics.ListCreateAPIView):
    queryset = Empresas.objects.all() # type: ignore
    serializer_class = EmpresasSerializer

class PlanesListAPIView(generics.ListCreateAPIView):
    queryset = Planes.objects.all() # type: ignore
    serializer_class = PlanesSerializer