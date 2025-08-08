from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import Group
from core.mixins import StandardResponseMixin
from .models import Usuarios
from .serializers import UsuariosSerializer, CustomPasswordChangeSerializer, GroupSerializer, UserPermissionsSerializer

class UsuariosListAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer

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
        return self.standard_create_response(
            request,
            *args,
            success_message="Usuario creado exitosamente",
            code="usuario_created",
            error_message="Error al crear el usuario",
            error_code="usuario_create_error",
            http_status=status.HTTP_201_CREATED,
            **kwargs
        )

class UsuarioDetailAPIView(StandardResponseMixin, generics.RetrieveAPIView):
    queryset = Usuarios.objects.all() # type: ignore
    serializer_class = UsuariosSerializer
    lookup_url_kwarg = 'usuario_id'

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
            return self.error_response(
                errors=str(e),
                message="Error al obtener el detalle del usuario",
                code="usuario_detail_error",
                http_status=status.HTTP_404_NOT_FOUND
            )

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


class GroupViewSet(StandardResponseMixin, generics.ListAPIView):
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

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Grupo creado exitosamente",
                code="group_created",
                http_status=201
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al crear el grupo",
                code="group_create_error",
                http_status=400
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return self.success_response(
                data=serializer.data,
                message="Detalle de grupo obtenido correctamente",
                code="group_detail",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al obtener el detalle del grupo",
                code="group_detail_error",
                http_status=404
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Grupo actualizado exitosamente",
                code="group_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar el grupo",
                code="group_update_error",
                http_status=400
            )

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message="Grupo actualizado parcialmente exitosamente",
                code="group_partial_updated",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al actualizar parcialmente el grupo",
                code="group_partial_update_error",
                http_status=400
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            group_name = instance.name
            instance.delete()
            return self.success_response(
                data={"deleted_group": group_name},
                message=f"Grupo '{group_name}' eliminado exitosamente",
                code="group_deleted",
                http_status=200
            )
        except Exception as e:
            return self.error_response(
                errors=str(e),
                message="Error al eliminar el grupo",
                code="group_delete_error",
                http_status=400
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