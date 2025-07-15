import django_filters
from .models import Tribunales


class TribunalesFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='iexact')
    id = django_filters.NumberFilter(field_name='id', lookup_expr='iexact')
    fecha = django_filters.DateFilter(field_name='fechaCreacion', lookup_expr='icontains')
    range = django_filters.RangeFilter(field_name='id')

    class Meta:
        model = Tribunales
        fields = ['nombre', 'id', 'fecha', 'range']
