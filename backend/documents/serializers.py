from rest_framework import serializers
from .models import (
    DocumentoSubido, 
    CampoDisponible, 
    PlantillaDocumento, 
    CampoPlantilla, 
    DocumentoGenerado,
    TipoPlantillaDocumento,
    CategoriaPlantillaDocumento,
    PlantillaCompartida,
    PlantillaFavorita,
    ClasificacionPlantillaGeneral,
    PlantillaGeneral,
    PlantillaGeneralCompartida
)


class DocumentoSubidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoSubido
        fields = '__all__'
        read_only_fields = ('id', 'fecha_subida')

class CampoDisponibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoDisponible
        fields = '__all__'

class TipoPlantillaDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPlantillaDocumento
        fields = '__all__'

class CategoriaPlantillaDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPlantillaDocumento
        fields = '__all__'

class ClasificacionPlantillaGeneralSerializer(serializers.ModelSerializer):
    total_paquetes = serializers.SerializerMethodField()
    paquetes_activos = serializers.SerializerMethodField()
    total_plantillas_en_categoria = serializers.SerializerMethodField()
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    
    class Meta:
        model = ClasificacionPlantillaGeneral
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', 'fecha_actualizacion')
    
    def get_total_paquetes(self, obj):
        """Retorna el total de paquetes en esta categoría"""
        return obj.get_paquetes_count()
    
    def get_paquetes_activos(self, obj):
        """Retorna el número de paquetes activos en esta categoría"""
        return obj.get_paquetes_activos().count()
    
    def get_total_plantillas_en_categoria(self, obj):
        """Retorna el total de plantillas en todos los paquetes de esta categoría"""
        return obj.get_total_plantillas_en_categoria()

class CampoPlantillaSerializer(serializers.ModelSerializer):
    campo_nombre = serializers.CharField(source='campo.nombre', read_only=True)
    campo_tipo = serializers.CharField(source='campo.tipo_dato', read_only=True)
    
    class Meta:
        model = CampoPlantilla
        fields = ['id', 'campo', 'nombre_variable', 'campo_nombre', 'campo_tipo']

class PlantillaDocumentoSerializer(serializers.ModelSerializer):
    campos_asociados = CampoPlantillaSerializer(many=True, read_only=True)
    tipo = TipoPlantillaDocumentoSerializer(read_only=True)
    clasificacion = ClasificacionPlantillaGeneralSerializer(read_only=True)
    categoria = CategoriaPlantillaDocumentoSerializer(read_only=True)
    tipo_info = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantillaDocumento
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion')
    
    def get_tipo_info(self, obj):
        if obj.tipo:
            return {
                'id': obj.tipo.id,
                'nombre': obj.tipo.nombre
            }
        return None

class DocumentoGeneradoSerializer(serializers.ModelSerializer):
    plantilla_nombre = serializers.CharField(source='plantilla.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = DocumentoGenerado
        fields = '__all__'
        read_only_fields = ('id', 'fecha_generacion', 'usuario')

class CrearPlantillaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    html_con_campos = serializers.CharField(required=False, allow_blank=True)
    tipo_id = serializers.IntegerField(required=False, allow_null=True)
    clasificacion_id = serializers.IntegerField(required=False, allow_null=True)
    categoria_id = serializers.IntegerField(required=False, allow_null=True)
    campos = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

class GenerarDocumentoSerializer(serializers.Serializer):
    plantilla_id = serializers.IntegerField()
    datos = serializers.DictField() 

class PlantillaCompartidaSerializer(serializers.ModelSerializer):
    plantilla_nombre = serializers.CharField(source='plantilla.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = PlantillaCompartida
        fields = ['id', 'plantilla', 'plantilla_nombre', 'usuario', 'usuario_username', 'permisos', 'fecha_compartida']

class PlantillaFavoritaSerializer(serializers.ModelSerializer):
    plantilla = PlantillaDocumentoSerializer(read_only=True)

    class Meta:
        model = PlantillaFavorita
        fields = '__all__'

class PlantillaGeneralSerializer(serializers.ModelSerializer):
    clasificacion = ClasificacionPlantillaGeneralSerializer(read_only=True)
    clasificacion_nombre = serializers.CharField(source='clasificacion.nombre', read_only=True)
    plantillas_incluidas = PlantillaDocumentoSerializer(many=True, read_only=True)
    total_plantillas = serializers.SerializerMethodField()
    creado_por_admin_nombre = serializers.CharField(source='creado_por_admin.get_full_name', read_only=True)
    usuarios_con_acceso = serializers.SerializerMethodField()
    plantillas_por_categoria = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantillaGeneral
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion', 'fecha_actualizacion')
    
    def get_total_plantillas(self, obj):
        """Retorna el total de plantillas incluidas en este paquete"""
        return obj.get_total_plantillas()
    
    def get_usuarios_con_acceso(self, obj):
        """Retorna la lista de usuarios que tienen acceso a este paquete"""
        usuarios = obj.get_usuarios_con_acceso()
        return [
            {
                'id': usuario.id,
                'username': usuario.username,
                'nombre_completo': usuario.get_full_name() or usuario.username
            }
            for usuario in usuarios
        ]
    
    def get_plantillas_por_categoria(self, obj):
         """Retorna las plantillas agrupadas por categoría"""
         return obj.get_plantillas_por_categoria()

class PlantillaGeneralCompartidaSerializer(serializers.ModelSerializer):
    plantilla_general_nombre = serializers.CharField(source='plantilla_general.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    asignado_por_nombre = serializers.CharField(source='asignado_por.get_full_name', read_only=True)
    esta_vigente = serializers.SerializerMethodField()
    plantillas_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantillaGeneralCompartida
        fields = '__all__'
        read_only_fields = ('id', 'fecha_asignacion', 'fecha_ultimo_acceso')
    
    def get_esta_vigente(self, obj):
        """Retorna si la asignación está vigente"""
        return obj.esta_vigente()
    
    def get_plantillas_disponibles(self, obj):
        """Retorna las plantillas disponibles en este paquete"""
        plantillas = obj.get_plantillas_disponibles()
        return [
            {
                'id': plantilla.id,
                'nombre': plantilla.nombre,
                'descripcion': plantilla.descripcion
            }
            for plantilla in plantillas
        ]

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
