from django.shortcuts import render, get_object_or_404
from api.serializers import *
from api.models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import generics


class TribunalesListAPIView(generics.ListAPIView):
    queryset = Tribunales.objects.all()
    serializer_class = TribunalesSerializer


@api_view(['GET'])
def tribunales_list(request):
    tribunales = Tribunales.objects.all()
    serializer = TribunalesSerializer(tribunales, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def tribunales_info(request):
    tribunales = Tribunales.objects.all()
    serializer = TribunalesInfoSerializer({
        'tribunales': tribunales,
        'count': len(tribunales)
    })
    return Response(serializer.data)


@api_view(['GET'])
def planes_list(request):
    planes = Planes.objects.all()
    serializer = PlanesSerializer(planes, many=True)
    return Response(serializer.data)


class UsuarioDetailAPIView(generics.RetrieveAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    lookup_url_kwarg = 'usuario_id'


@api_view(['GET'])
def usuario_detail(request, pk):
    usuario = get_object_or_404(Usuarios, pk=pk)
    serializer = UsuariosSerializer(usuario)
    return Response(serializer.data)


@api_view(['GET'])
def empresas_list(request):
    empresas = Empresas.objects.all()
    serializer = EmpresasSerializer(empresas, many=True)
    return Response(serializer.data)


