from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter

from .filters import TribunalesFilter
from .models import Empresas, Planes, Tribunales
from .serializers import EmpresasSerializer, PlanesSerializer, TribunalesSerializer
from rest_framework.response import Response
from .paginations import CustomPagination
from core.mixins import StandardResponseMixin

class EmpresasListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Empresas.objects.all() # type: ignore
    serializer_class = EmpresasSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    #^quecomience
    search_fields = ['^nombre', 'rut', 'fechaCreacion']
    ordering_fields = ['id', 'nombre']

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated = self.get_paginated_response(serializer.data).data
                return self.success_response(
                    data=paginated,
                    message="Listado paginado de empresas",
                    code="empresas_list",
                    http_status=200
                )
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Listado de empresas obtenido correctamente",
                code="empresas_list",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el listado de empresas",
                code="empresas_list_error",
                http_status=500
            )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Empresa creada exitosamente",
                code="empresa_created",
                http_status=201
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al crear la empresa",
                code="empresa_create_error",
                http_status=400
            )

class PlanesListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Planes.objects.all() # type: ignore
    serializer_class = PlanesSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated = self.get_paginated_response(serializer.data).data
                return self.success_response(
                    data=paginated,
                    message="Listado paginado de planes",
                    code="planes_list",
                    http_status=200
                )
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Listado de planes obtenido correctamente",
                code="planes_list",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el listado de planes",
                code="planes_list_error",
                http_status=500
            )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Plan creado exitosamente",
                code="plan_created",
                http_status=201
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al crear el plan",
                code="plan_create_error",
                http_status=400
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
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated = self.get_paginated_response(serializer.data).data
                return self.success_response(
                    data=paginated,
                    message="Listado paginado de tribunales",
                    code="tribunales_list",
                    http_status=200
                )
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Listado de tribunales obtenido correctamente",
                code="tribunales_list",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el listado de planes",
                code="planes_list_error",
                http_status=500
            )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return self.success_response(
                data=response.data,
                message="Tribunal creado exitosamente",
                code="tribunal_created",
                http_status=201
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al crear el tribunal",
                code="tribunal_create_error",
                http_status=400
            )
