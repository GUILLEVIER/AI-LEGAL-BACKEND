from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import Usuarios
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

# Ocultar modelos no deseados del admin si están registrados
for model in [TokenProxy, Site, EmailAddress, SocialToken, SocialAccount, SocialApp]:
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
