from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from core.mixins import StandardResponseMixin
from .models import Usuarios
from .serializers import UsuariosSerializer, UsuariosCreateSerializer, CustomPasswordChangeSerializer, GroupSerializer, UserPermissionsSerializer

class UsuariosViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action in ['create', 'update', 'partial_update']:
            return UsuariosCreateSerializer
        return UsuariosSerializer

    def get_queryset(self):
        """
        Filtra los usuarios según el tipo de usuario:
        - Admin/Superuser: Ve todos los usuarios (excepto él mismo)
        - Usuario regular: Ve solo usuarios de su misma empresa (excepto él mismo)
        """
        user = self.request.user
        
        # Si es admin o superuser, mostrar todos los usuarios excepto él mismo
        if user.is_staff or user.is_superuser:
            return Usuarios.objects.exclude(id=user.id)
        
        # Si es usuario regular, filtrar por empresa y excluir al usuario actual
        if hasattr(user, 'empresa') and user.empresa:
            return Usuarios.objects.filter(empresa=user.empresa).exclude(id=user.id)
        else:
            # Si el usuario no tiene empresa asignada, no mostrar ningún usuario
            return Usuarios.objects.none()

    def get_object(self):
        """Verificar permisos antes de obtener el objeto"""
        obj = super().get_object()
        user = self.request.user
        
        # Para eliminación, prevenir auto-eliminación
        if self.action == 'destroy' and obj.id == user.id:
            raise PermissionDenied("No puedes eliminar tu propia cuenta")
        
        # Si es admin o superuser, puede hacer cualquier operación
        if user.is_staff or user.is_superuser:
            return obj
        
        # Si es usuario regular, solo puede operar con usuarios de su misma empresa
        if hasattr(user, 'empresa') and user.empresa:
            if obj.empresa == user.empresa:
                return obj
        
        # Si no tiene permisos, lanzar excepción
        action_messages = {
            'retrieve': 'ver',
            'update': 'editar',
            'partial_update': 'editar',
            'destroy': 'eliminar'
        }
        action_name = action_messages.get(self.action, 'acceder a')
        raise PermissionDenied(f"No tienes permisos para {action_name} este usuario")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self.paginated_list_response(
            request,
            queryset,
            self.get_serializer_class(),
            paginated_message="Listado paginado de usuarios",
            unpaginated_message="Listado de usuarios obtenido correctamente",
            code="usuarios_list",
            error_code="usuarios_list_error"
        )

    def create(self, request, *args, **kwargs):
        try:
            # Copiar los datos de la solicitud
            data = request.data.copy()
            user = request.user
            
            # Lógica de asignación de empresa
            if user.is_staff or user.is_superuser:
                # Si es admin, puede seleccionar la empresa (mantener el valor enviado)
                pass
            else:
                # Si es usuario regular, asignar automáticamente su empresa
                if hasattr(user, 'empresa') and user.empresa:
                    data['empresa'] = user.empresa.id
                else:
                    # Si el usuario no tiene empresa, no puede crear usuarios
                    return self.error_response(
                        errors="No tienes permisos para crear usuarios",
                        message="Usuario sin empresa no puede crear otros usuarios",
                        code="usuario_create_forbidden",
                        http_status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            usuario = serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Usuario creado exitosamente",
                code="usuario_created",
                http_status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return self.handle_exception(e)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Detalle de usuario obtenido correctamente",
                code="usuario_detail",
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            return self.handle_exception(e)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Copiar los datos de la solicitud
            data = request.data.copy()
            user = request.user
            
            # Lógica de asignación de empresa para actualización
            if not (user.is_staff or user.is_superuser):
                # Si es usuario regular, no puede cambiar la empresa
                if 'empresa' in data:
                    data.pop('empresa')
            
            # Validar que no se esté intentando cambiar campos sensibles sin permisos
            sensitive_fields = ['is_staff', 'is_superuser', 'groups', 'user_permissions']
            if not (user.is_staff or user.is_superuser):
                for field in sensitive_fields:
                    if field in data:
                        data.pop(field)
            
            serializer = self.get_serializer(instance, data=data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)
            usuario = serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message="Usuario actualizado exitosamente",
                code="usuario_updated",
                http_status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            usuario_info = {
                'id': instance.id,
                'username': instance.username,
                'email': instance.email,
                'full_name': f"{instance.first_name} {instance.last_name}".strip()
            }
            
            instance.delete()
            
            return self.success_response(
                data=usuario_info,
                message=f"Usuario '{usuario_info['username']}' eliminado exitosamente",
                code="usuario_deleted",
                http_status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_exception(e)

    @action(detail=True, methods=['get'], url_path='permissions')
    def permissions(self, request, pk=None):
        """Acción personalizada para obtener permisos de un usuario"""
        try:
            instance = self.get_object()
            serializer = UserPermissionsSerializer(instance)
            
            # Información adicional sobre el resumen de permisos
            total_groups = instance.groups.count()
            total_direct_permissions = instance.user_permissions.count()
            total_all_permissions = len(serializer.data['all_permissions'])
            
            response_data = {
                'user_info': {
                    'id': instance.id,
                    'username': instance.username,
                    'email': instance.email,
                    'full_name': f"{instance.first_name} {instance.last_name}".strip(),
                    'empresa': serializer.data['empresa']
                },
                'permissions_summary': {
                    'total_groups': total_groups,
                    'total_direct_permissions': total_direct_permissions,
                    'total_all_permissions': total_all_permissions,
                    'is_superuser': instance.is_superuser,
                    'is_staff': instance.is_staff
                },
                'groups': serializer.data['groups'],
                'direct_permissions': serializer.data['user_permissions'],
                'all_permissions': serializer.data['all_permissions']
            }
            
            return self.success_response(
                data=response_data,
                message=f"Permisos del usuario '{instance.username}' obtenidos correctamente",
                code="user_permissions_detail",
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            return self.handle_exception(e)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Endpoint para obtener información completa del usuario actual"""
        try:
            user = request.user
            
            # Información de la empresa
            empresa_info = None
            if hasattr(user, 'empresa') and user.empresa:
                empresa_info = {
                    'id': user.empresa.id,
                    'nombre': user.empresa.nombre,
                    'rut': user.empresa.rut,
                    'correo': user.empresa.correo,
                    'fecha_creacion': user.empresa.fecha_creacion,
                    'plan': {
                        'id': user.empresa.plan.id,
                        'tipo_plan': user.empresa.plan.tipo_plan,
                        'nombre': user.empresa.plan.nombre,
                        'precio': user.empresa.plan.precio,
                        'cantidad_users': user.empresa.plan.cantidad_users,
                        'cantidad_escritos': user.empresa.plan.cantidad_escritos,
                        'cantidad_demandas': user.empresa.plan.cantidad_demandas,
                        'cantidad_contratos': user.empresa.plan.cantidad_contratos,
                        'cantidad_consultas': user.empresa.plan.cantidad_consultas,
                        'fecha_creacion': user.empresa.plan.fecha_creacion
                    } if user.empresa.plan else None
                }
            
            # Información de grupos
            groups_info = []
            for group in user.groups.all():
                groups_info.append({
                    'id': group.id,
                    'name': group.name,
                    'permissions_count': group.permissions.count()
                })
            
            # Información de permisos directos
            direct_permissions = []
            for perm in user.user_permissions.all():
                direct_permissions.append({
                    'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'content_type': {
                        'app_label': perm.content_type.app_label,
                        'model': perm.content_type.model
                    }
                })
            
            # Todos los permisos (grupos + directos)
            all_permissions = list(user.get_all_permissions())
            
            # Estadísticas de permisos
            permissions_stats = {
                'total_groups': user.groups.count(),
                'total_direct_permissions': user.user_permissions.count(),
                'total_all_permissions': len(all_permissions),
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
            
            # Información general del usuario
            user_info = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
            
            # Respuesta completa
            response_data = {
                'user_info': user_info,
                'empresa': empresa_info,
                'groups': groups_info,
                'permissions': {
                    'direct_permissions': direct_permissions,
                    'all_permissions': all_permissions,
                    'stats': permissions_stats
                },
                'profile_completion': {
                    'has_first_name': bool(user.first_name),
                    'has_last_name': bool(user.last_name),
                    'has_email': bool(user.email),
                    'has_empresa': bool(hasattr(user, 'empresa') and user.empresa),
                    'completion_percentage': self._calculate_profile_completion(user)
                }
            }
            
            return self.success_response(
                data=response_data,
                message="Información del usuario actual obtenida correctamente",
                code="current_user_info",
                http_status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener la información del usuario actual",
                code="current_user_info_error",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_profile_completion(self, user):
        """Calcula el porcentaje de completitud del perfil"""
        fields_to_check = [
            bool(user.first_name),
            bool(user.last_name),
            bool(user.email),
            bool(hasattr(user, 'empresa') and user.empresa)
        ]
        completed_fields = sum(fields_to_check)
        total_fields = len(fields_to_check)
        return round((completed_fields / total_fields) * 100, 2)

class CustomLoginView(StandardResponseMixin, LoginView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            # Si el login fue exitoso (status 200 o 201)
            if response.status_code in [200, 201]:
                return self.success_response(
                    data=response.data,
                    message="Login exitoso",
                    code="login_success",
                    http_status=response.status_code
                )
            else:
                # Si hubo error, extrae el mensaje de error de forma segura
                error_msg = "Credenciales inválidas"
                if hasattr(response, 'data') and response.data:
                    if isinstance(response.data, dict):
                        error_msg = (
                            response.data.get('non_field_errors') or 
                            response.data.get('detail') or 
                            "Credenciales inválidas"
                        )
                        # Si es una lista, toma el primer elemento
                        if isinstance(error_msg, list) and error_msg:
                            error_msg = error_msg[0]
                
                return self.error_response(
                    errors=error_msg,
                    message="Credenciales inválidas",
                    code="login_failed",
                    http_status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            # Manejo de cualquier excepción no prevista
            return self.error_response(
                errors="Credenciales inválidas",
                message="Credenciales inválidas",
                code="login_error",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

class CustomTokenRefreshView(StandardResponseMixin, TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                return self.success_response(
                    data=response.data,
                    message="Token refrescado exitosamente",
                    code="token_refresh_success",
                    http_status=status.HTTP_200_OK
                )
            else:
                error_msg = "Token inválido o expirado"
                if hasattr(response, 'data') and response.data and isinstance(response.data, dict):
                    error_msg = response.data.get('detail') or "Token inválido o expirado"
                    if isinstance(error_msg, list) and error_msg:
                        error_msg = error_msg[0]
                
                return self.error_response(
                    errors=error_msg,
                    message="Token inválido o expirado",
                    code="token_refresh_failed",
                    http_status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return self.error_response(
                errors="Token inválido o expirado",
                message="Token inválido o expirado",
                code="token_refresh_error",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

class CustomTokenVerifyView(StandardResponseMixin, TokenVerifyView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                return self.success_response(
                    data=response.data,
                    message="Token verificado exitosamente",
                    code="token_verify_success",
                    http_status=status.HTTP_200_OK
                )
            else:
                error_msg = "Token inválido"
                if hasattr(response, 'data') and response.data and isinstance(response.data, dict):
                    error_msg = response.data.get('detail') or "Token inválido"
                    if isinstance(error_msg, list) and error_msg:
                        error_msg = error_msg[0]
                
                return self.error_response(
                    errors=error_msg,
                    message="Token inválido",
                    code="token_verify_failed",
                    http_status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return self.error_response(
                errors="Token inválido",
                message="Token inválido",
                code="token_verify_error",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

class CustomPasswordChangeView(StandardResponseMixin, PasswordChangeView):
    serializer_class = CustomPasswordChangeSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code in [200, 201]:
                return self.success_response(
                    data=response.data,
                    message="Contraseña cambiada exitosamente",
                    code="password_change_success",
                    http_status=response.status_code
                )
            else:
                error_msg = "No se pudo cambiar la contraseña"
                if hasattr(response, 'data') and response.data and isinstance(response.data, dict):
                    error_msg = (
                        response.data.get('non_field_errors') or 
                        response.data.get('detail') or 
                        "No se pudo cambiar la contraseña"
                    )
                    if isinstance(error_msg, list) and error_msg:
                        error_msg = error_msg[0]
                
                return self.error_response(
                    errors=error_msg,
                    message="No se pudo cambiar la contraseña",
                    code="password_change_failed",
                    http_status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return self.error_response(
                errors="No se pudo cambiar la contraseña",
                message="No se pudo cambiar la contraseña",
                code="password_change_error",
                http_status=status.HTTP_400_BAD_REQUEST
            )

class CustomLogoutView(StandardResponseMixin, LogoutView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code in [200, 201]:
                return self.success_response(
                    data=response.data,
                    message="Logout exitoso",
                    code="logout_success",
                    http_status=response.status_code
                )
            else:
                error_msg = "No se pudo cerrar sesión"
                if hasattr(response, 'data') and response.data and isinstance(response.data, dict):
                    error_msg = response.data.get('detail') or "No se pudo cerrar sesión"
                    if isinstance(error_msg, list) and error_msg:
                        error_msg = error_msg[0]
                
                return self.error_response(
                    errors=error_msg,
                    message="No se pudo cerrar sesión",
                    code="logout_failed",
                    http_status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return self.error_response(
                errors="No se pudo cerrar sesión",
                message="No se pudo cerrar sesión",
                code="logout_error",
                http_status=status.HTTP_400_BAD_REQUEST
            )


class GroupAPIView(StandardResponseMixin, generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message="Listado de grupos obtenido correctamente",
                code="groups_list",
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el listado de grupos",
                code="groups_list_error",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPermissionsAPIView(StandardResponseMixin, generics.RetrieveAPIView):
    """Vista para obtener los permisos de un usuario específico"""
    queryset = Usuarios.objects.all()
    serializer_class = UserPermissionsSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'usuario_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            # Información adicional sobre el resumen de permisos
            total_groups = instance.groups.count()
            total_direct_permissions = instance.user_permissions.count()
            total_all_permissions = len(serializer.data['all_permissions'])
            
            response_data = {
                'user_info': {
                    'id': instance.id,
                    'username': instance.username,
                    'email': instance.email,
                    'full_name': f"{instance.first_name} {instance.last_name}".strip(),
                    'empresa': serializer.data['empresa']
                },
                'permissions_summary': {
                    'total_groups': total_groups,
                    'total_direct_permissions': total_direct_permissions,
                    'total_all_permissions': total_all_permissions,
                    'is_superuser': instance.is_superuser,
                    'is_staff': instance.is_staff
                },
                'groups': serializer.data['groups'],
                'direct_permissions': serializer.data['user_permissions'],
                'all_permissions': serializer.data['all_permissions']
            }
            
            return self.success_response(
                data=response_data,
                message=f"Permisos del usuario '{instance.username}' obtenidos correctamente",
                code="user_permissions_detail",
                http_status=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener los permisos del usuario",
                code="user_permissions_error",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )