from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from rest_framework.authtoken.models import TokenProxy
from .models import *


admin.site.unregister({TokenProxy, Site, EmailAddress, SocialToken, SocialAccount, SocialApp})


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Additional Info',
            {
                'fields': (
                    'empresa',
                )
            }
        )
    )


admin.site.register(Usuarios, CustomUserAdmin)

admin.site.register(Perfiles)
admin.site.register(Planes)
admin.site.register(Tribunales)
admin.site.register(TipoDocumento)
admin.site.register(Documentos)
admin.site.register(Favoritos)
admin.site.register(Compartir)
admin.site.register(Clasificacion)
admin.site.register(Plantillas)


@admin.register(Empresas)
class EmpresasAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ("nombre__icontains", )
    list_display = ("id", "plan", "rut", "nombre", "correo")
    list_filter = ("id", "plan", "rut", "nombre", "correo")
