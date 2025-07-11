from rest_framework import serializers
from .models import (
    TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos,
    Clasificacion, Plantillas
)
from users.serializers import UsuariosSerializer

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = '__all__'

class DocumentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documentos
        fields = '__all__'
        read_only_fields = ['created_by']

class FavoritosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favoritos
        fields = '__all__'
        read_only_fields = ['usuario']

class CompartirSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compartir
        fields = '__all__'
        read_only_fields = ['usuario']

class EscritosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escritos
        fields = '__all__'
        read_only_fields = ['created_by']

class DemandasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demandas
        fields = '__all__'
        read_only_fields = ['created_by']

class ContratosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contratos
        fields = '__all__'
        read_only_fields = ['created_by']

class ClasificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clasificacion
        fields = '__all__'

class PlantillasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plantillas
        fields = '__all__'