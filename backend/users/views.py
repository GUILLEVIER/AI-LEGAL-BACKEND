from rest_framework import generics
from .models import Usuarios
from .serializers import UsuariosSerializer

class UsuariosListAPIView(generics.ListCreateAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer

class UsuarioDetailAPIView(generics.RetrieveAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer
    lookup_url_kwarg = 'usuario_id'