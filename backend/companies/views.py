from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter

from .filters import TribunalesFilter
from .models import Empresas, Planes, Tribunales
from .serializers import EmpresasSerializer, PlanesSerializer, TribunalesSerializer
from rest_framework.response import Response
from .paginations import CustomPagination
from core.mixins import StandardResponseMixin

class EmpresasViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = Empresas.objects.all() # type: ignore
    serializer_class = EmpresasSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    #^quecomience
    search_fields = ['^nombre', 'rut', 'fechaCreacion']
    ordering_fields = ['id', 'nombre']
    #http_method_names = ['get', 'head', 'options']

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Detalle de empresa obtenida correctamente",
                code="empresa_detail",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el detalle de la empresa",
                code="empresa_detail_error",
                http_status=404
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de empresas",
            unpaginated_message="Listado de empresas obtenido correctamente",
            code="empresas_list",
            error_code="empresas_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Empresa creada exitosamente",
            code="empresa_created",
            error_message="Error al crear la empresa",
            error_code="empresa_create_error",
            http_status=201,
            **kwargs
        )

    def retrieve(self, request, *args, **kwargs):
        return self.error_response(
                errors="Método no permitido.",
                message="Método no permitido.",
                code="empresa_detail_error",
                http_status=405
            )

    def partial_update(self, request, *args, **kwargs):
        return self.error_response({'detail': 'Método no permitido.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return self.error_response({'detail': 'Método no permitido.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class EmpresasListAPIView(StandardResponseMixin, generics.ListAPIView):
    queryset = Empresas.objects.all() # type: ignore
    serializer_class = EmpresasSerializer

class PlanesListAPIView(StandardResponseMixin, generics.ListAPIView):
    queryset = Planes.objects.all() # type: ignore
    serializer_class = PlanesSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de planes",
            unpaginated_message="Listado de planes obtenido correctamente",
            code="planes_list",
            error_code="planes_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Plan creado exitosamente",
            code="plan_created",
            error_message="Error al crear el plan",
            error_code="plan_create_error",
            http_status=201,
            **kwargs
        )

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
"""
class TribunalesViewset(viewsets.ModelViewSet):
    queryset = Tribunales.objects.all()
    serializer_class = TribunalesSerializer
    pagination_class = CustomPagination
    #filterset_fields = ['nombre', 'id']
    filterset_class = TribunalesFilter
"""


class TribunalesListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Tribunales.objects.all() # type: ignore
    serializer_class = TribunalesSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de tribunales",
            unpaginated_message="Listado de tribunales obtenido correctamente",
            code="tribunales_list",
            error_code="tribunales_list_error"
        )

    def create(self, request, *args, **kwargs):
        return self.standard_create_response(
            request,
            *args,
            success_message="Tribunal creado exitosamente",
            code="tribunal_created",
            error_message="Error al crear el tribunal",
            error_code="tribunal_create_error",
            http_status=201,
            **kwargs
        )
