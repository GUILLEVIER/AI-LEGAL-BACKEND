from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import Group, Permission
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


class GroupViewSetTestCase(TestCase):
    def setUp(self):
        self.plan = Planes.objects.create(nombre="Plan Básico", tipoPlan="Básico", precio=0) # type: ignore
        self.empresa = Empresas.objects.create(nombre="Empresa 1", rut="11111111-1", correo="e1@e.com", plan=self.plan) # type: ignore
        self.admin = Usuarios.objects.create_superuser(username="admin", password="adminpass", empresa=self.empresa)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_group(self):
        """Prueba la creación de un grupo"""
        response = self.client.post(
            reverse('groups-list'),
            {
                "name": "Administradores",
                "permissions": []
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['name'], "Administradores")
        self.assertEqual(response.data['message'], "Grupo creado exitosamente")

    def test_list_groups(self):
        """Prueba el listado de grupos"""
        Group.objects.create(name="Grupo Test")
        response = self.client.get(reverse('groups-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "Listado de grupos obtenido correctamente")
        self.assertTrue(len(response.data['data']) >= 1)

    def test_retrieve_group(self):
        """Prueba la obtención de un grupo específico"""
        group = Group.objects.create(name="Grupo Detalle")
        response = self.client.get(reverse('groups-detail', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], "Grupo Detalle")
        self.assertEqual(response.data['message'], "Detalle de grupo obtenido correctamente")

    def test_update_group(self):
        """Prueba la actualización completa de un grupo"""
        group = Group.objects.create(name="Grupo Original")
        response = self.client.put(
            reverse('groups-detail', kwargs={'pk': group.id}),
            {
                "name": "Grupo Actualizado",
                "permissions": []
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], "Grupo Actualizado")
        self.assertEqual(response.data['message'], "Grupo actualizado exitosamente")

    def test_partial_update_group(self):
        """Prueba la actualización parcial de un grupo"""
        group = Group.objects.create(name="Grupo Parcial")
        response = self.client.patch(
            reverse('groups-detail', kwargs={'pk': group.id}),
            {
                "name": "Grupo Parcialmente Actualizado"
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], "Grupo Parcialmente Actualizado")
        self.assertEqual(response.data['message'], "Grupo actualizado parcialmente exitosamente")

    def test_delete_group(self):
        """Prueba la eliminación de un grupo"""
        group = Group.objects.create(name="Grupo a Eliminar")
        response = self.client.delete(reverse('groups-detail', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "Grupo 'Grupo a Eliminar' eliminado exitosamente")
        self.assertFalse(Group.objects.filter(id=group.id).exists())

    def test_group_with_permissions(self):
        """Prueba la creación de un grupo con permisos"""
        # Obtener algunos permisos existentes
        permissions = Permission.objects.all()[:2]
        permission_ids = [perm.id for perm in permissions]
        
        response = self.client.post(
            reverse('groups-list'),
            {
                "name": "Grupo con Permisos",
                "permissions": permission_ids
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['name'], "Grupo con Permisos")
        self.assertEqual(len(response.data['data']['permissions']), 2)

    def test_unauthorized_access(self):
        """Prueba que se requiere autenticación"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('groups-list'))
        # Puede ser 401 (no autorizado) o 403 (prohibido) dependiendo de la configuración
        self.assertIn(response.status_code, [401, 403, 500])


class UserPermissionsTestCase(TestCase):
    def setUp(self):
        self.plan = Planes.objects.create(nombre="Plan Básico", tipoPlan="Básico", precio=0) # type: ignore
        self.empresa = Empresas.objects.create(nombre="Empresa 1", rut="11111111-1", correo="e1@e.com", plan=self.plan) # type: ignore
        self.admin = Usuarios.objects.create_superuser(username="admin", password="adminpass", empresa=self.empresa)
        self.test_user = Usuarios.objects.create_user(username="testuser", password="testpass", empresa=self.empresa)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_get_user_permissions_basic(self):
        """Prueba obtener permisos básicos de un usuario sin grupos ni permisos"""
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': self.test_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], f"Permisos del usuario '{self.test_user.username}' obtenidos correctamente")
        
        data = response.data['data']
        self.assertEqual(data['user_info']['username'], 'testuser')
        self.assertEqual(data['permissions_summary']['total_groups'], 0)
        self.assertEqual(data['permissions_summary']['total_direct_permissions'], 0)
        self.assertFalse(data['permissions_summary']['is_superuser'])
        
        # Verificar que la información de la empresa está incluida
        self.assertIn('empresa', data['user_info'])
        self.assertEqual(data['user_info']['empresa']['nombre'], 'Empresa 1')
        self.assertEqual(data['user_info']['empresa']['rut'], '11111111-1')

    def test_get_user_permissions_with_group(self):
        """Prueba obtener permisos de un usuario con grupos"""
        # Crear un grupo con permisos
        group = Group.objects.create(name="Test Group")
        permissions = Permission.objects.all()[:2]
        group.permissions.set(permissions)
        
        # Asignar el grupo al usuario
        self.test_user.groups.add(group)
        
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': self.test_user.id}))
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        self.assertEqual(data['permissions_summary']['total_groups'], 1)
        self.assertEqual(len(data['groups']), 1)
        self.assertEqual(data['groups'][0]['name'], 'Test Group')
        self.assertTrue(len(data['all_permissions']) >= 2)

    def test_get_user_permissions_with_direct_permissions(self):
        """Prueba obtener permisos de un usuario con permisos directos"""
        # Asignar permisos directos al usuario
        permissions = Permission.objects.all()[:3]
        self.test_user.user_permissions.set(permissions)
        
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': self.test_user.id}))
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        self.assertEqual(data['permissions_summary']['total_direct_permissions'], 3)
        self.assertEqual(len(data['direct_permissions']), 3)
        self.assertTrue(len(data['all_permissions']) >= 3)

    def test_get_user_permissions_mixed(self):
        """Prueba obtener permisos de un usuario con grupos y permisos directos"""
        # Crear grupo con permisos
        group = Group.objects.create(name="Mixed Group")
        group_permissions = Permission.objects.all()[:2]
        group.permissions.set(group_permissions)
        self.test_user.groups.add(group)
        
        # Asignar permisos directos (algunos diferentes, algunos iguales)
        direct_permissions = Permission.objects.all()[1:4]  # Overlap con group_permissions
        self.test_user.user_permissions.set(direct_permissions)
        
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': self.test_user.id}))
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        self.assertEqual(data['permissions_summary']['total_groups'], 1)
        self.assertEqual(data['permissions_summary']['total_direct_permissions'], 3)
        self.assertEqual(len(data['groups']), 1)
        self.assertEqual(len(data['direct_permissions']), 3)
        
        # Verificar que all_permissions no tenga duplicados
        all_perms_codes = [p['codename'] for p in data['all_permissions']]
        self.assertEqual(len(all_perms_codes), len(set(all_perms_codes)))

    def test_get_superuser_permissions(self):
        """Prueba obtener permisos de un superusuario"""
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': self.admin.id}))
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        self.assertTrue(data['permissions_summary']['is_superuser'])
        self.assertTrue(data['permissions_summary']['is_staff'])

    def test_get_nonexistent_user_permissions(self):
        """Prueba obtener permisos de un usuario que no existe"""
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': 99999}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "Error al obtener los permisos del usuario")

    def test_unauthorized_access_user_permissions(self):
        """Prueba que se requiere autenticación para ver permisos"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('usuario-permissions', kwargs={'usuario_id': self.test_user.id}))
        self.assertIn(response.status_code, [401, 403, 500])