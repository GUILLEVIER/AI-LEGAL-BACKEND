from django.db import models
from django.contrib.auth.models import AbstractUser
from companies.models import Empresas


class Usuarios(AbstractUser):
    empresa = models.ForeignKey(Empresas, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'usuarios'
        verbose_name_plural = 'Usuarios'

class Perfil(models.Model):
    TIPO_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX')
    ]

    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE)
    descargar = models.CharField(max_length=10, choices=TIPO_CHOICES, default='pdf')
    interlineado = models.DecimalField(max_digits=10, decimal_places=1, default=1.0)
    footer = models.TextField(blank=True)
    abogado_uno = models.CharField(max_length=100, blank=True)
    abogado_dos = models.CharField(max_length=100, blank=True)
    rut_uno = models.CharField(max_length=100, blank=True)
    rut_dos = models.CharField(max_length=100, blank=True)
    representante_banco = models.CharField(max_length=100, blank=True)
    rut_representante = models.CharField(max_length=100, blank=True)
    banco = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = True
        db_table = 'perfiles'
        verbose_name_plural = 'Perfiles'