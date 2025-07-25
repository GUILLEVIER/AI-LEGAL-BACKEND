from django.contrib import admin
from .models import Empresas, Planes

from unfold.admin import ModelAdmin


@admin.register(Empresas)
class EmpresasAdmin(ModelAdmin):
    ordering = ['id']
    search_fields = ("nombre__icontains", )
    list_display = ("id", "plan", "rut", "nombre", "correo")
    list_filter = ("id", "plan", "rut", "nombre", "correo")


@admin.register(Planes)
class PlanesAdmin(ModelAdmin):
    pass
