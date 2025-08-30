from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import Usuarios, Perfil
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from allauth.account.models import EmailAddress
from rest_framework.authtoken.admin import TokenProxy
from django.contrib.admin.sites import NotRegistered

from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

admin.site.unregister(Group)


class CustomUserAdmin(UserAdmin, ModelAdmin):
    fieldsets = (
        *UserAdmin.fieldsets, # type: ignore
        (
            'Additional Info',
            {
                'fields': (
                    'empresa',
                )
            }
        )
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


admin.site.register(Usuarios, CustomUserAdmin)

@admin.register(Group)
class GroupAdmin(GroupAdmin, ModelAdmin):
    pass


@admin.register(Perfil)
class PerfilAdmin(ModelAdmin):
    list_display = ('id', 'usuario', 'get_usuario_empresa', 'descargar', 'interlineado')
    list_filter = ('descargar', 'usuario__empresa')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__email')
    readonly_fields = ('id',)
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario',)
        }),
        ('Configuración de Descarga', {
            'fields': ('descargar', 'interlineado')
        }),
        ('Información de Abogados', {
            'fields': ('abogado_uno', 'rut_uno', 'abogado_dos', 'rut_dos')
        }),
        ('Información Bancaria', {
            'fields': ('representante_banco', 'rut_representante', 'banco')
        }),
        ('Footer', {
            'fields': ('footer',)
        })
    )
    
    def get_usuario_empresa(self, obj):
        """Obtener la empresa del usuario"""
        return obj.usuario.empresa.nombre if obj.usuario.empresa else 'Sin empresa'
    get_usuario_empresa.short_description = 'Empresa'
    get_usuario_empresa.admin_order_field = 'usuario__empresa__nombre'
    
    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related('usuario', 'usuario__empresa')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar usuarios según permisos del admin"""
        if db_field.name == "usuario":
            # Si el usuario admin no es superuser, solo mostrar usuarios de su empresa
            if not request.user.is_superuser and hasattr(request.user, 'empresa') and request.user.empresa:
                kwargs["queryset"] = Usuarios.objects.filter(empresa=request.user.empresa)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Ocultar modelos no deseados del admin si están registrados
for model in [TokenProxy, Site, EmailAddress, SocialToken, SocialAccount, SocialApp]:
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
