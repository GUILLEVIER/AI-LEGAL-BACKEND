from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.serializers import PasswordChangeSerializer
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


class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover los campos originales
        if 'new_password1' in self.fields:
            del self.fields['new_password1']
        if 'new_password2' in self.fields:
            del self.fields['new_password2']

    def validate(self, attrs):
        # Validar que las contraseñas nuevas coincidan
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': _('Las contraseñas no coinciden.')
            })
        
        # Mapear a los campos esperados por el serializer padre
        attrs['new_password1'] = new_password
        attrs['new_password2'] = confirm_password
        
        # Llamar a la validación del padre
        return super().validate(attrs)