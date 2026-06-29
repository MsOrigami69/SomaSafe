from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import IncidenteForm
from .models import Incidente


@override_settings(SECURE_SSL_REDIRECT=False)
class IncidenteAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='operador',
            password='clave-segura-123',
        )

    def test_private_views_require_login(self):
        private_urls = [
            reverse('dashboard'),
            reverse('registrar_incidente'),
            reverse('lista_incidentes'),
        ]

        for url in private_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response['Location'])

    def test_authenticated_user_can_create_incident(self):
        self.client.login(username='operador', password='clave-segura-123')

        response = self.client.post(
            reverse('registrar_incidente'),
            {
                'tipo': 'accidente',
                'fecha': date.today(),
                'descripcion': 'Caída controlada reportada en zona de carga.',
                'ubicacion': 'Zona norte',
                'estado': 'pendiente',
                'riesgo': 'medio',
            },
        )

        self.assertRedirects(response, reverse('lista_incidentes'))
        self.assertEqual(Incidente.objects.count(), 1)

    def test_logout_view(self):
        self.client.login(username='operador', password='clave-segura-123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_search_and_filters(self):
        self.client.login(username='operador', password='clave-segura-123')
        
        # Crear incidentes de prueba
        Incidente.objects.create(
            tipo='accidente',
            fecha=date.today(),
            descripcion='Derrame de aceite en taller principal.',
            ubicacion='Taller Mecánico',
            estado='pendiente',
            riesgo='medio',
            creado_por=self.user
        )
        Incidente.objects.create(
            tipo='condicion_insegura',
            fecha=date.today(),
            descripcion='Cable pelado expuesto en pasillo C.',
            ubicacion='Pasillo C',
            estado='resuelto',
            riesgo='alto',
            creado_por=self.user,
            fecha_resolucion=date.today()
        )

        # Buscar por texto "Cable"
        response = self.client.get(reverse('lista_incidentes') + '?q=Cable')
        self.assertEqual(len(response.context['incidentes']), 1)
        self.assertEqual(response.context['incidentes'][0].ubicacion, 'Pasillo C')

        # Filtrar por estado "resuelto"
        response = self.client.get(reverse('lista_incidentes') + '?estado=resuelto')
        self.assertEqual(len(response.context['incidentes']), 1)
        self.assertEqual(response.context['incidentes'][0].estado, 'resuelto')

        # Filtrar por riesgo "medio"
        response = self.client.get(reverse('lista_incidentes') + '?riesgo=medio')
        self.assertEqual(len(response.context['incidentes']), 1)
        self.assertEqual(response.context['incidentes'][0].riesgo, 'medio')


class IncidenteFormTests(TestCase):
    def valid_data(self):
        return {
            'tipo': 'accidente',
            'fecha': date.today(),
            'descripcion': 'Descripción válida del incidente reportado.',
            'ubicacion': 'Planta 1',
            'estado': 'pendiente',
            'riesgo': 'bajo',
        }

    def test_rejects_future_date(self):
        data = self.valid_data()
        data['fecha'] = date.today() + timedelta(days=1)

        form = IncidenteForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('fecha', form.errors)

    def test_rejects_short_description(self):
        data = self.valid_data()
        data['descripcion'] = 'corto'

        form = IncidenteForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)
