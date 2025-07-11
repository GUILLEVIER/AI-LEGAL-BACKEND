from django.db import models
from django.contrib.auth.models import AbstractUser


class Tribunales(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=250, null=False, blank=False)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tribunales'
        verbose_name_plural = 'Tribunales'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)


class Planes(models.Model):
    id = models.AutoField(primary_key=True)
    tipoPlan = models.CharField(max_length=200, blank=False, null=False)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    precio = models.FloatField()
    cantidadUsers = models.IntegerField(null=False, blank=False, default=1)
    cantidadEscritos = models.IntegerField(null=False, blank=False, default=1)
    cantidadDemandas = models.IntegerField(null=False, blank=False, default=1)
    cantidadContratos = models.IntegerField(null=False, blank=False, default=1)
    cantidadConsultas = models.IntegerField(null=False, blank=False, default=1)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'planes'
        verbose_name_plural = 'Planes'

    #@property
    #def documentos_total(self):
    #    return self.cantidadContratos + self.cantidadEscritos + self.cantidadDemandas

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)


class Empresas(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Planes, null=False, blank=False, on_delete=models.CASCADE)
    rut = models.CharField(max_length=15, null=False, blank=False)
    nombre = models.CharField(max_length=250, null=False, blank=False)
    correo = models.CharField(max_length=250, null=False, blank=False)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'empresas'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)


class Perfiles(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=250, null=False, blank=False)
    entidad = models.CharField(max_length=250, null=False, blank=False)
    rutEntidad = models.CharField(max_length=15, null=False, blank=False)
    representante = models.CharField(max_length=250, null=False, blank=False)
    rutRepresentante = models.CharField(max_length=15, null=False, blank=False)
    mandato = models.CharField(max_length=1000, null=False, blank=False)
    informacion = models.CharField(max_length=1000, null=True, blank=True)
    descripcion = models.CharField(max_length=1000, null=False, blank=False)
    header = models.CharField(max_length=1000, null=True, blank=True)
    footer = models.CharField(max_length=1000, null=True, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'perfiles'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)


class Usuarios(AbstractUser):
    empresa = models.ForeignKey(Empresas, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'usuarios'
        verbose_name_plural = 'Usuarios'


class TipoDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tipo_documento'
        verbose_name_plural = 'Tipo de Documento'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)


class Documentos(models.Model):
    id = models.AutoField(primary_key=True)
    tipoDocumento = models.ForeignKey(TipoDocumento, null=False, blank=False, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    descripcion = models.CharField(max_length=1000, blank=True, null=True)
    plantilla = models.FileField(blank=True, null=True)
    campos = models.JSONField(blank=True, null=True)
    version = models.IntegerField(null=False, blank=False, default=1)
    created_by = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='created_by')
    updated_by = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_by')
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'documentos'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)

class Favoritos(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, null=False, blank=False, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documentos, null=False, blank=False, on_delete=models.CASCADE)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'favoritos'
        verbose_name_plural = 'Favoritos'


class Compartir(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='usuario')
    documento = models.ForeignKey(Documentos, null=False, blank=False, on_delete=models.CASCADE)
    usuarios = models.ManyToManyField(Usuarios, blank=True)
    empresas = models.ManyToManyField(Empresas, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'compartir'
        verbose_name_plural = 'Compartir'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.documento)


class Escritos(models.Model):
    id = models.AutoField(primary_key=True)
    documento = models.ForeignKey(Documentos, null=False, blank=False, on_delete=models.CASCADE)
    tribunales = models.ForeignKey(Tribunales, null=False, blank=False, on_delete=models.CASCADE)
    rol = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'escritos'
        verbose_name_plural = 'Escritos'


class Demandas(models.Model):
    id = models.AutoField(primary_key=True)
    documento = models.ForeignKey(Documentos, null=False, blank=False, on_delete=models.CASCADE)
    tribunales = models.ForeignKey(Tribunales, null=False, blank=False, on_delete=models.CASCADE)
    operacion = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'demandas'
        verbose_name_plural = 'Demandas'


class Contratos(models.Model):
    id = models.AutoField(primary_key=True)
    documento = models.ForeignKey(Documentos, null=False, blank=False, on_delete=models.CASCADE)
    tribunales = models.ForeignKey(Tribunales, null=False, blank=False, on_delete=models.CASCADE)
    created_by = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'contratos'
        verbose_name_plural = 'Contratos'


class Clasificacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'clasificacion'
        verbose_name_plural = 'Clasificacion'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)


class Plantillas(models.Model):
    id = models.AutoField(primary_key=True)
    clasificacion = models.ForeignKey(Clasificacion, null=False, blank=False, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, blank=False, null=False)
    descripcion = models.CharField(max_length=1000, blank=True, null=True)
    documentos = models.ManyToManyField(Documentos, blank=True)
    fechaCreacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'plantillas'
        verbose_name_plural = 'Plantillas'

    def __str__(self):
        txt = "{0}"
        return txt.format(self.nombre)
