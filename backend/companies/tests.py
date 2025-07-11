from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from companies.models import Empresas, Planes
from users.models import Usuarios

class EmpresasTestCase(TestCase):
    def setUp(self):
        self.plan = Planes.objects.create(nombre="Plan Básico", tipoPlan="Básico", precio=0) # type: ignore
        self.client = APIClient()
        self.admin = Usuarios.objects.create_superuser(username="admin", password="adminpass")

    def test_create_and_list_empresas(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('empresas-list'),
            {
                "nombre": "Empresa Test",
                "rut": "12345678-9",
                "correo": "empresa@test.com",
                "plan": self.plan.id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        response = self.client.get(reverse('empresas-list')) # type: ignore
        self.assertTrue(any(e['nombre'] == "Empresa Test" for e in response.data['results'])) # type: ignore

class PlanesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuarios.objects.create_superuser(username="admin", password="adminpass")

    def test_create_and_list_planes(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('planes-list'),
            {
                "nombre": "Plan Test",
                "tipoPlan": "Premium",
                "precio": 100.0
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201) # type: ignore
        response = self.client.get(reverse('planes-list')) # type: ignore
        self.assertTrue(any(p['nombre'] == "Plan Test" for p in response.data['results'])) # type: ignore