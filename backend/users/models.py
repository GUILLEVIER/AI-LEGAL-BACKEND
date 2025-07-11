from django.db import models
from django.contrib.auth.models import AbstractUser
from companies.models import Empresas


class Usuarios(AbstractUser):
    empresa = models.ForeignKey(Empresas, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'usuarios'
        verbose_name_plural = 'Usuarios'