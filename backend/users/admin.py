from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuarios
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from allauth.account.models import EmailAddress
from rest_framework.authtoken.admin import TokenProxy
from django.contrib.admin.sites import NotRegistered

class CustomUserAdmin(UserAdmin):
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


admin.site.register(Usuarios, CustomUserAdmin)

# Ocultar modelos no deseados del admin si están registrados
for model in [TokenProxy, Site, EmailAddress, SocialToken, SocialAccount, SocialApp]:
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
