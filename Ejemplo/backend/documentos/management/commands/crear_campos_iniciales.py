from django.core.management.base import BaseCommand
from documentos.models import CampoDisponible

class Command(BaseCommand):
    help = 'Crea campos iniciales de ejemplo para el sistema'

    def handle(self, *args, **options):
        campos_iniciales = [
            {'nombre': 'nombre_cliente', 'tipo_dato': 'texto'},
            {'nombre': 'apellido_cliente', 'tipo_dato': 'texto'},
            {'nombre': 'email_cliente', 'tipo_dato': 'texto'},
            {'nombre': 'telefono_cliente', 'tipo_dato': 'texto'},
            {'nombre': 'direccion_cliente', 'tipo_dato': 'texto'},
            {'nombre': 'fecha_contrato', 'tipo_dato': 'fecha'},
            {'nombre': 'fecha_vencimiento', 'tipo_dato': 'fecha'},
            {'nombre': 'monto_contrato', 'tipo_dato': 'numero'},
            {'nombre': 'numero_contrato', 'tipo_dato': 'texto'},
            {'nombre': 'empresa', 'tipo_dato': 'texto'},
            {'nombre': 'cargo', 'tipo_dato': 'texto'},
            {'nombre': 'ciudad', 'tipo_dato': 'texto'},
            {'nombre': 'pais', 'tipo_dato': 'texto'},
            {'nombre': 'codigo_postal', 'tipo_dato': 'texto'},
        ]

        campos_creados = 0
        for campo_data in campos_iniciales:
            campo, created = CampoDisponible.objects.get_or_create(
                nombre=campo_data['nombre'],
                defaults={'tipo_dato': campo_data['tipo_dato']}
            )
            if created:
                campos_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Campo creado: {campo.nombre} ({campo.tipo_dato})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Campo ya existe: {campo.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {campos_creados} campos nuevos')
        ) 