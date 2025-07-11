from rest_framework import serializers
from .models import Usuarios
from companies.serializers import EmpresasSerializer

class UsuariosSerializer(serializers.ModelSerializer):
    empresa = EmpresasSerializer(read_only=True)

    class Meta:
        model = Usuarios
        fields = (
            "id", "username", "email", "first_name", "last_name", "empresa"
        )
        read_only_fields = ["empresa"]