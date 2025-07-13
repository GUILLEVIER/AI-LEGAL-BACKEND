from rest_framework import generics
from .models import Empresas, Planes, Tribunales
from .serializers import EmpresasSerializer, PlanesSerializer, TribunalesSerializer

class EmpresasListAPIView(generics.ListCreateAPIView):
    queryset = Empresas.objects.all() # type: ignore
    serializer_class = EmpresasSerializer

class PlanesListAPIView(generics.ListCreateAPIView):
    queryset = Planes.objects.all() # type: ignore
    serializer_class = PlanesSerializer


"""
# mixins
class TribunalesView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Tribunales.objects.all() # type: ignore
    serializer_class = TribunalesSerializer

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)


class TribunalesDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Tribunales.objects.all()
    serializer_class = TribunalesSerializer

    def get(self, request, pk):
        return self.retrieve(request, pk)

    def put(self, request, pk):
        return self.update(request, pk)

    def delete(self, request, pk):
        return self.destroy(request, pk)
"""


# generics
class TribunalesListAPIView(generics.ListCreateAPIView):
    queryset = Tribunales.objects.all() # type: ignore
    serializer_class = TribunalesSerializer


class TribunalesDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tribunales.objects.all()
    serializer_class = TribunalesSerializer
    lookup_field = 'pk'
