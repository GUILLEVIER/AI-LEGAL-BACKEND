from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter

from .filters import TribunalesFilter
from .models import Empresas, Planes, Tribunales
from .serializers import EmpresasSerializer, PlanesSerializer, TribunalesSerializer
from rest_framework.response import Response
from .paginations import CustomPagination

class EmpresasListAPIView(generics.ListCreateAPIView):
    queryset = Empresas.objects.all() # type: ignore
    serializer_class = EmpresasSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    #^quecomience
    search_fields = ['^nombre', 'rut', 'fechaCreacion']
    ordering_fields = ['id', 'nombre']

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

"""
# generics
class TribunalesListAPIView(generics.ListCreateAPIView):
    queryset = Tribunales.objects.all() # type: ignore
    serializer_class = TribunalesSerializer


class TribunalesDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tribunales.objects.all()
    serializer_class = TribunalesSerializer
    lookup_field = 'pk'
"""

"""
# viewsets
class TribunalesViewset(viewsets.ViewSet):
    def list(self, request):
        querySet = Tribunales.objects.all()
        serializer = TribunalesSerializer(querySet, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = TribunalesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

    def retrieve(self, request, pk=None):
        tribunales = get_object_or_404(Tribunales, pk=pk)
        serializer = TribunalesSerializer(tribunales, data=request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        tribunales = get_object_or_404(Tribunales, pk=pk)
        serializer = TribunalesSerializer(tribunales, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk=None):
        tribunales = get_object_or_404(Tribunales, pk=pk)
        tribunales.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""

class TribunalesViewset(viewsets.ModelViewSet):
    queryset = Tribunales.objects.all()
    serializer_class = TribunalesSerializer
    pagination_class = CustomPagination
    #filterset_fields = ['nombre', 'id']
    filterset_class = TribunalesFilter
