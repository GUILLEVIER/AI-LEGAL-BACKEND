from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from companies.models import Empresas, Planes
from users.models import Usuarios
from documents.models import (
    TipoDocumento, Documentos, Favoritos, Compartir, Escritos, Demandas, Contratos,
    Plantillas, Clasificacion
)

class DocumentsBaseTestCase(TestCase):
    def setUp(self):
        self.plan = Planes.objects.create(nombre="Plan Básico", tipoPlan="Básico", precio=0) # type: ignore
        self.empresa1 = Empresas.objects.create(nombre="Empresa 1", rut="11111111-1", correo="e1@e.com", plan=self.plan) # type: ignore
        self.empresa2 = Empresas.objects.create(nombre="Empresa 2", rut="22222222-2", correo="e2@e.com", plan=self.plan) # type: ignore
        self.user1 = Usuarios.objects.create_user(username="user1", password="pass1", empresa=self.empresa1)
        self.user2 = Usuarios.objects.create_user(username="user2", password="pass2", empresa=self.empresa2)
        self.tipo_doc = TipoDocumento.objects.create(nombre="Tipo 1") # type: ignore
        self.clasificacion = Clasificacion.objects.create(nombre="Clasif 1") # type: ignore
        self.tribunal = None
        if getattr(self, 'tribunal_required', False):
            from documents.models import Tribunales
            self.tribunal = Tribunales.objects.create(nombre="Tribunal 1") # type: ignore
        self.client = APIClient()

class DocumentosTestCase(DocumentsBaseTestCase):
    def test_user_can_only_create_document_for_own_company(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse('documentos-list'),
            {
                "nombre": "Doc Empresa 1",
                "tipoDocumento": self.tipo_doc.id,
                "descripcion": "Test",
                "version": 1
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        doc = Documentos.objects.get(nombre="Doc Empresa 1") # type: ignore
        self.assertEqual(doc.created_by, self.user1)
        self.assertEqual(doc.created_by.empresa, self.empresa1)

    def test_user_cannot_see_documents_of_other_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Empresa 1",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('documentos-list'))
        self.assertNotIn(doc.nombre, [d['nombre'] for d in response.data['results']]) # type: ignore

class ContratosTestCase(DocumentsBaseTestCase):
    tribunal_required = True
    def test_user_can_only_create_contrato_for_own_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Contrato",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user1)
        data = {
            "documento": doc.id,
        }
        if self.tribunal is not None:
            data["tribunales"] = self.tribunal.id
        response = self.client.post(
            reverse('contratos-list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        contrato = Contratos.objects.get(documento=doc) # type: ignore
        self.assertEqual(contrato.created_by, self.user1)
        self.assertEqual(contrato.created_by.empresa, self.empresa1)

    def test_user_cannot_see_contratos_of_other_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Contrato",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        contrato = Contratos.objects.create( # type: ignore
            documento=doc,
            tribunales=self.tribunal,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('contratos-list'))
        self.assertNotIn(contrato.id, [c['id'] for c in response.data['results']]) # type: ignore

class FavoritosTestCase(DocumentsBaseTestCase):
    def test_user_can_only_create_favorito_for_own_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Favorito",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse('favoritos-list'),
            {
                "documento": doc.id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        favorito = Favoritos.objects.get(documento=doc) # type: ignore
        self.assertEqual(favorito.usuario, self.user1)
        self.assertEqual(favorito.usuario.empresa, self.empresa1)

    def test_user_cannot_see_favoritos_of_other_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Favorito",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        favorito = Favoritos.objects.create( # type: ignore
            documento=doc,
            usuario=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('favoritos-list'))
        self.assertNotIn(favorito.id, [f['id'] for f in response.data['results']]) # type: ignore

class CompartirTestCase(DocumentsBaseTestCase):
    def test_user_can_only_create_compartir_for_own_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Compartir",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse('compartir-list'),
            {
                "documento": doc.id,
                "usuarios": [self.user1.id],
                "empresas": [self.empresa1.id]
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        compartir = Compartir.objects.get(documento=doc) # type: ignore
        self.assertEqual(compartir.usuario, self.user1)
        self.assertIn(self.empresa1, compartir.empresas.all())

    def test_user_cannot_see_compartir_of_other_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Compartir",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        compartir = Compartir.objects.create( # type: ignore
            documento=doc,
            usuario=self.user1
        )
        compartir.empresas.add(self.empresa1)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('compartir-list'))
        self.assertNotIn(compartir.id, [c['id'] for c in response.data['results']]) # type: ignore

class EscritosTestCase(DocumentsBaseTestCase):
    tribunal_required = True
    def test_user_can_only_create_escrito_for_own_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Escrito",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user1)
        data = {
            "documento": doc.id,
            "rol": "R1"
        }
        if self.tribunal is not None:
            data["tribunales"] = self.tribunal.id
        response = self.client.post(
            reverse('escritos-list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        escrito = Escritos.objects.get(documento=doc) # type: ignore
        self.assertEqual(escrito.created_by, self.user1)
        self.assertEqual(escrito.created_by.empresa, self.empresa1)

    def test_user_cannot_see_escritos_of_other_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Escrito",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        escrito = Escritos.objects.create( # type: ignore
            documento=doc,
            tribunales=self.tribunal,
            rol="R1",
            created_by=self.user1
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('escritos-list'))
        self.assertNotIn(escrito.id, [e['id'] for e in response.data['results']]) # type: ignore

class DemandasTestCase(DocumentsBaseTestCase):
    tribunal_required = True
    def test_user_can_only_create_demanda_for_own_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Demanda",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        self.client.force_authenticate(user=self.user1)
        data = {
            "documento": doc.id,
            "operacion": "Op1"
        }
        if self.tribunal is not None:
            data["tribunales"] = self.tribunal.id
        response = self.client.post(
            reverse('demandas-list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        demanda = Demandas.objects.get(documento=doc) # type: ignore
        self.assertEqual(demanda.created_by, self.user1)
        self.assertEqual(demanda.created_by.empresa, self.empresa1)

    def test_user_cannot_see_demandas_of_other_company(self):
        doc = Documentos.objects.create( # type: ignore
            nombre="Doc Demanda",
            tipoDocumento=self.tipo_doc,
            descripcion="Test",
            version=1,
            created_by=self.user1
        ) # type: ignore
        demanda = Demandas.objects.create( # type: ignore
            documento=doc,
            tribunales=self.tribunal,
            operacion="Op1",
            created_by=self.user1
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('demandas-list'))
        self.assertNotIn(demanda.id, [d['id'] for d in response.data['results']]) # type: ignore

class PlantillasTestCase(DocumentsBaseTestCase):
    def test_create_and_list_plantillas(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse('plantillas-list'),
            {
                "clasificacion": self.clasificacion.id,
                "nombre": "Plantilla 1"
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        response = self.client.get(reverse('plantillas-list'))
        self.assertTrue(any(p['nombre'] == "Plantilla 1" for p in response.data['results'])) # type: ignore

class ClasificacionTestCase(DocumentsBaseTestCase):
    def test_create_and_list_clasificacion(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse('clasificacion-list'),
            {"nombre": "Clasif Test"},
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        response = self.client.get(reverse('clasificacion-list'))
        self.assertTrue(any(c['nombre'] == "Clasif Test" for c in response.data['results'])) # type: ignore

class TipoDocumentoTestCase(DocumentsBaseTestCase):
    def test_create_and_list_tipodocumento(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse('tipodocumento-list'),
            {"nombre": "Tipo Test"},
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        response = self.client.get(reverse('tipodocumento-list'))
        self.assertTrue(any(t['nombre'] == "Tipo Test" for t in response.data['results'])) # type: ignore