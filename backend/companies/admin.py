from django.contrib import admin
from .models import Empresas, Planes

@admin.register(Empresas)
class EmpresasAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ("nombre__icontains", )
    list_display = ("id", "plan", "rut", "nombre", "correo")
    list_filter = ("id", "plan", "rut", "nombre", "correo")
admin.site.register(Planes)
