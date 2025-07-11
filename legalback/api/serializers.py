from rest_framework import serializers
from .models import Tribunales, Planes, Usuarios, Empresas


class TribunalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunales
        fields = (
            'nombre',
            'fechaCreacion',
        )


class PlanesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planes
        fields = (
            "nombre",
            "precio",
            "cantidadUsers",
            "cantidadEscritos",
            "cantidadDemandas",
            "cantidadContratos",
            "cantidadConsultas",
            #"documentos_total",
        )


class EmpresasSerializer(serializers.ModelSerializer):
    #plan = PlanesSerializer(read_only=True)
    plan_nombre = serializers.CharField(source='plan.nombre')
    plan_precio = serializers.DecimalField(
        max_digits=10,
        decimal_places=0,
        source='plan.precio'
    )

    class Meta:
        model = Empresas
        fields = (
            'id',
            'plan_nombre',
            'plan_precio',
            'rut',
            'nombre',
            'correo',
            'fechaCreacion',
        )


class UsuariosSerializer(serializers.ModelSerializer):
    empresa = EmpresasSerializer(read_only=True)
    #empresa = serializers.CharField(source='empresa.nombre')

    class Meta:
        model = Usuarios
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "empresa",
        )


class TribunalesInfoSerializer(serializers.Serializer):
    tribunales = TribunalesSerializer(many=True)
    count = serializers.IntegerField()
