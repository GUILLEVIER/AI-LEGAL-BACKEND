from rest_framework import serializers
from .models import Empresas, Planes, Tribunales

class PlanesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planes
        fields = '__all__'

class EmpresasSerializer(serializers.ModelSerializer):
    plan_nombre = serializers.CharField(source='plan.nombre', read_only=True)
    plan_precio = serializers.DecimalField(
        max_digits=10, decimal_places=0, source='plan.precio', read_only=True
    )

    class Meta:
        model = Empresas
        fields = (
            'id', 'plan', 'plan_nombre', 'plan_precio', 'rut', 'nombre', 'correo', 'fechaCreacion'
        )


class TribunalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunales
        fields = '__all__'