from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
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


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')
        read_only_fields = ('id',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Incluir información de permisos de manera más legible
        if instance.permissions.exists():
            representation['permissions'] = [
                {
                    'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'content_type': perm.content_type.model
                }
                for perm in instance.permissions.all()
            ]
        else:
            representation['permissions'] = []
        return representation


class UserPermissionsSerializer(serializers.ModelSerializer):
    """Serializer para mostrar los permisos de un usuario con detalle de grupos"""
    groups = GroupSerializer(many=True, read_only=True)
    user_permissions = serializers.SerializerMethodField()
    all_permissions = serializers.SerializerMethodField()
    empresa = EmpresasSerializer(read_only=True)
    
    class Meta:
        model = Usuarios
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'empresa', 'groups', 'user_permissions', 'all_permissions')
        read_only_fields = ('id', 'username', 'email', 'first_name', 'last_name', 'empresa')

    def get_user_permissions(self, obj):
        """Obtiene los permisos asignados directamente al usuario"""
        return [
            {
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'content_type': perm.content_type.model,
                'app_label': perm.content_type.app_label
            }
            for perm in obj.user_permissions.all()
        ]

    def get_all_permissions(self, obj):
        """Obtiene todos los permisos del usuario (directos + de grupos)"""
        all_perms = obj.get_all_permissions()
        permissions_detail = []
        
        # Obtener permisos directos
        direct_permissions = obj.user_permissions.all()
        for perm in direct_permissions:
            permissions_detail.append({
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'content_type': perm.content_type.model,
                'app_label': perm.content_type.app_label,
                'source': 'direct',
                'source_name': 'Usuario'
            })
        
        # Obtener permisos de grupos
        for group in obj.groups.all():
            for perm in group.permissions.all():
                permissions_detail.append({
                    'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'content_type': perm.content_type.model,
                    'app_label': perm.content_type.app_label,
                    'source': 'group',
                    'source_name': group.name
                })
        
        # Eliminar duplicados manteniendo la información de origen
        unique_permissions = {}
        for perm in permissions_detail:
            key = f"{perm['app_label']}.{perm['codename']}"
            if key not in unique_permissions:
                unique_permissions[key] = perm
            else:
                # Si ya existe, agregar información de múltiples fuentes
                existing = unique_permissions[key]
                if existing['source'] != perm['source']:
                    existing['source'] = 'multiple'
                    if 'sources' not in existing:
                        existing['sources'] = [{'type': existing['source'], 'name': existing['source_name']}]
                    existing['sources'].append({'type': perm['source'], 'name': perm['source_name']})
        
        return list(unique_permissions.values())