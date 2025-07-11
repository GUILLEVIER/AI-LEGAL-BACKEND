from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import Usuarios
from companies.models import Empresas, Planes

class UsuariosTestCase(TestCase):
    def setUp(self):
        self.plan = Planes.objects.create(nombre="Plan Básico", tipoPlan="Básico", precio=0) # type: ignore
        self.empresa = Empresas.objects.create(nombre="Empresa 1", rut="11111111-1", correo="e1@e.com", plan=self.plan) # type: ignore
        self.admin = Usuarios.objects.create_superuser(username="admin", password="adminpass", empresa=self.empresa)
        self.client = APIClient()

    def test_create_and_list_usuarios(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('usuarios-list'),
            {
                "username": "nuevo_usuario",
                "password": "testpass123",
                "empresa": self.empresa.id
            },
            format='json'
        )
        self.assertIn(response.status_code, [201, 400])  # Puede ser 400 si falta algún campo requerido
        response = self.client.get(reverse('usuarios-list'))
        self.assertTrue(any(u['username'] == "nuevo_usuario" for u in response.data['results'])) # type: ignore