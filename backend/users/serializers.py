from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.serializers import PasswordChangeSerializer
from .models import Usuarios, Perfil
from companies.serializers import EmpresasSerializer

class UsuariosSerializer(serializers.ModelSerializer):
    empresa = EmpresasSerializer(read_only=True)
    grupos = serializers.SerializerMethodField()

    class Meta:
        model = Usuarios
        fields = (
            "id", "username", "email", "first_name", "last_name", "empresa", "grupos"
        )
        read_only_fields = ["empresa", "grupos"]

    def get_grupos(self, obj):
        """Obtiene los grupos a los que pertenece el usuario"""
        grupos = [group.name for group in obj.groups.all()]
        return ", ".join(grupos) if grupos else "Sin grupo"



class UsuariosCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para la creación de usuarios que permite escribir empresa y grupos"""
    empresa = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    grupos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = Usuarios
        fields = (
            "id", "username", "email", "first_name", "last_name", "empresa", "password", "grupos"
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        """Validación general para manejar empresa y grupos"""
        # Validar empresa
        if 'empresa' in attrs and attrs['empresa'] == 0:
            attrs['empresa'] = None
        
        # Validar grupos
        if 'grupos' in attrs:
            valid_group_ids = []
            for group_id in attrs['grupos']:
                if group_id != 0:
                    try:
                        Group.objects.get(id=group_id)
                        valid_group_ids.append(group_id)
                    except Group.DoesNotExist:
                        continue
            attrs['grupos'] = valid_group_ids
        
        return attrs
    
    def create(self, validated_data):
        from companies.models import Empresas
        
        # Extraer la contraseña, empresa y grupos para manejarlos por separado
        password = validated_data.pop('password', None)
        empresa_id = validated_data.pop('empresa', None)
        groups_data = validated_data.pop('grupos', [])
        
        # Convertir empresa_id a objeto Empresa si se proporcionó
        if empresa_id:
            try:
                validated_data['empresa'] = Empresas.objects.get(id=empresa_id)
            except Empresas.DoesNotExist:
                pass  # Se mantiene como None si no existe
        
        # Crear el usuario
        usuario = Usuarios.objects.create(**validated_data)
        
        # Establecer la contraseña si se proporcionó
        if password:
            usuario.set_password(password)
            usuario.save()
        
        # Asignar grupos si se proporcionaron
        if groups_data:
            usuario.groups.set(groups_data)
        
        return usuario


class UsuariosUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para la actualización de usuarios que permite escribir empresa y grupos"""
    empresa = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    grupos = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = Usuarios
        fields = (
            "id", "username", "email", "first_name", "last_name", "empresa", "grupos"
        )
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }
    
    def validate(self, attrs):
        """Validación general para manejar empresa y grupos"""
        # Validar empresa
        if 'empresa' in attrs and attrs['empresa'] == 0:
            attrs['empresa'] = None
        
        # Validar grupos
        if 'grupos' in attrs:
            valid_group_ids = []
            for group_id in attrs['grupos']:
                if group_id != 0:
                    try:
                        Group.objects.get(id=group_id)
                        valid_group_ids.append(group_id)
                    except Group.DoesNotExist:
                        continue
            attrs['grupos'] = valid_group_ids
        
        return attrs
    
    def update(self, instance, validated_data):
        from companies.models import Empresas
        
        # Extraer empresa y grupos si están presentes
        empresa_id = validated_data.pop('empresa', None)
        groups_data = validated_data.pop('grupos', None)
        
        # Convertir empresa_id a objeto Empresa si se proporcionó
        if empresa_id is not None:
            if empresa_id:
                try:
                    validated_data['empresa'] = Empresas.objects.get(id=empresa_id)
                except Empresas.DoesNotExist:
                    pass  # Se mantiene el valor actual si no existe
            else:
                validated_data['empresa'] = None
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Manejar grupos si se proporcionaron
        if groups_data is not None:
            # Limpiar grupos existentes y asignar los nuevos
            instance.groups.clear()
            if groups_data:  # Si hay grupos para asignar
                instance.groups.set(groups_data)
        
        return instance


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


class PerfilSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Perfil"""
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuarios.objects.all())
    usuario_info = UsuariosSerializer(source='usuario', read_only=True)
    
    class Meta:
        model = Perfil
        fields = (
            'id', 'usuario', 'usuario_info', 'descargar', 'interlineado', 
            'footer', 'abogado_uno', 'abogado_dos', 'rut_uno', 'rut_dos',
            'representante_banco', 'rut_representante', 'banco'
        )
        read_only_fields = ('id',)
    
    def validate_interlineado(self, value):
        """Validar que el interlineado esté en un rango válido"""
        if value < 0.5 or value > 3.0:
            raise serializers.ValidationError(
                "El interlineado debe estar entre 0.5 y 3.0"
            )
        return value


class PerfilCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para la creación de perfiles"""
    
    class Meta:
        model = Perfil
        fields = (
            'usuario', 'descargar', 'interlineado', 'footer', 
            'abogado_uno', 'abogado_dos', 'rut_uno', 'rut_dos',
            'representante_banco', 'rut_representante', 'banco'
        )
    
    def validate_usuario(self, value):
        """Validar que el usuario no tenga ya un perfil"""
        if Perfil.objects.filter(usuario=value).exists():
            raise serializers.ValidationError(
                "Este usuario ya tiene un perfil asociado"
            )
        return value
    
    def validate_interlineado(self, value):
        """Validar que el interlineado esté en un rango válido"""
        if value < 0.5 or value > 3.0:
            raise serializers.ValidationError(
                "El interlineado debe estar entre 0.5 y 3.0"
            )
        return value


class PerfilUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para la actualización de perfiles"""
    
    class Meta:
        model = Perfil
        fields = (
            'descargar', 'interlineado', 'footer', 
            'abogado_uno', 'abogado_dos', 'rut_uno', 'rut_dos',
            'representante_banco', 'rut_representante', 'banco'
        )
    
    def validate_interlineado(self, value):
        """Validar que el interlineado esté en un rango válido"""
        if value < 0.5 or value > 3.0:
            raise serializers.ValidationError(
                "El interlineado debe estar entre 0.5 y 3.0"
            )
        return value