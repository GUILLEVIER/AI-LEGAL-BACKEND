from rest_framework import serializers
from .models import (
    DocumentoSubido, 
    CampoDisponible, 
    PlantillaDocumento, 
    CampoPlantilla, 
    DocumentoGenerado,
    TipoPlantillaDocumento,
    PlantillaCompartida,
    PlantillaFavorita,
    ClasificacionPlantillaGeneral,
    PlantillaGeneral
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

class CampoPlantillaSerializer(serializers.ModelSerializer):
    campo_nombre = serializers.CharField(source='campo.nombre', read_only=True)
    campo_tipo = serializers.CharField(source='campo.tipo_dato', read_only=True)
    
    class Meta:
        model = CampoPlantilla
        fields = ['id', 'campo', 'nombre_variable', 'campo_nombre', 'campo_tipo']

class PlantillaDocumentoSerializer(serializers.ModelSerializer):
    campos_asociados = CampoPlantillaSerializer(many=True, read_only=True)
    tipo = TipoPlantillaDocumentoSerializer(read_only=True)
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

class ClasificacionPlantillaGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClasificacionPlantillaGeneral
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion')

class PlantillaGeneralSerializer(serializers.ModelSerializer):
    clasificacion = ClasificacionPlantillaGeneralSerializer(read_only=True)
    clasificacion_nombre = serializers.CharField(source='clasificacion.nombre', read_only=True)
    documentos = PlantillaDocumentoSerializer(many=True, read_only=True)
    total_documentos = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantillaGeneral
        fields = '__all__'
        read_only_fields = ('id', 'fecha_creacion')
    
    def get_total_documentos(self, obj):
        return obj.documentos.count()

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
