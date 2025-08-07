from django.db import models


class Tribunales(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=250, null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tribunales'
        verbose_name_plural = 'Tribunales'

    def __str__(self):
        return self.nombre


class Planes(models.Model):
    id = models.AutoField(primary_key=True)
    tipoPlan = models.CharField(max_length=200, blank=False, null=False)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    precio = models.FloatField()
    cantidadUsers = models.IntegerField(null=False, blank=False, default=1) # type: ignore
    cantidadEscritos = models.IntegerField(null=False, blank=False, default=1) # type: ignore
    cantidadDemandas = models.IntegerField(null=False, blank=False, default=1) # type: ignore
    cantidadContratos = models.IntegerField(null=False, blank=False, default=1) # type: ignore
    cantidadConsultas = models.IntegerField(null=False, blank=False, default=1) # type: ignore
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'planes'
        verbose_name_plural = 'Planes'

    def __str__(self):
        return self.nombre

    #@property
    #def documentos_total(self):
    #    return self.cantidadContratos + self.cantidadEscritos + self.cantidadDemandas

class Empresas(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Planes, null=False, blank=False, on_delete=models.CASCADE)
    rut = models.CharField(max_length=15, null=False, blank=False)
    nombre = models.CharField(max_length=250, null=False, blank=False)
    correo = models.CharField(max_length=250, null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'empresas'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre