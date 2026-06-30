from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.booking.models import Appointment, MasterProfile, Service, ServiceCategory

User = get_user_model()


@override_settings(ALLOWED_HOSTS=['testserver'])
class AppointmentHistoryTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.master_api = APIClient()
        self.other_client_api = APIClient()

        self.client_user = User.objects.create_user(
            username='client1',
            email='client1@test.com',
            password='pass12345',
            first_name='Client',
            last_name='One',
            phone='+998900000101',
        )
        self.other_client = User.objects.create_user(
            username='client2',
            email='client2@test.com',
            password='pass12345',
            first_name='Client',
            last_name='Two',
            phone='+998900000102',
        )
        self.master_user = User.objects.create_user(
            username='master1',
            email='master1@test.com',
            password='pass12345',
            first_name='Master',
            last_name='One',
            phone='+998900000103',
            is_master=True,
        )
        self.master_profile = MasterProfile.objects.create(user=self.master_user)
        self.category = ServiceCategory.objects.create(name='Soch', is_active=True)
        self.service = Service.objects.create(
            category=self.category,
            name='Soch kesish',
            duration_minutes=60,
            price=100000,
            is_active=True,
        )
        self.booking_date = date.today() + timedelta(days=3)
        self.start_time = '10:00'

        self.client_api.force_authenticate(user=self.client_user)
        self.master_api.force_authenticate(user=self.master_user)
        self.other_client_api.force_authenticate(user=self.other_client)

    def _create_booking(self, api_client=None):
        api_client = api_client or self.client_api
        return api_client.post(
            '/api/booking/appointments/',
            {
                'master': self.master_profile.id,
                'service': self.service.id,
                'date': self.booking_date.isoformat(),
                'start_time': self.start_time,
            },
            format='json',
        )

    def test_booking_appears_in_client_and_master_history(self):
        create_response = self._create_booking()
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        appointment_id = create_response.data['id']
        self.assertEqual(create_response.data['client'], self.client_user.id)

        client_history = self.client_api.get('/api/auth/profile/history/')
        self.assertEqual(client_history.status_code, status.HTTP_200_OK)
        client_ids = [item['id'] for item in client_history.data]
        self.assertIn(appointment_id, client_ids)

        master_history = self.master_api.get('/api/auth/profile/history/')
        self.assertEqual(master_history.status_code, status.HTTP_200_OK)
        master_ids = [item['id'] for item in master_history.data]
        self.assertIn(appointment_id, master_ids)

    def test_duplicate_slot_is_rejected(self):
        first = self._create_booking()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self._create_booking(api_client=self.other_client_api)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        error_text = str(second.data)
        self.assertIn('band qilingan', error_text.lower())

    def test_profile_history_returns_unpaginated_list(self):
        self._create_booking()
        response = self.client_api.get('/api/auth/profile/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_booking_list_endpoint_filters_by_role(self):
        self._create_booking()
        client_list = self.client_api.get('/api/booking/appointments/')
        self.assertEqual(client_list.status_code, status.HTTP_200_OK)
        results = client_list.data.get('results', client_list.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['client'], self.client_user.id)

        master_list = self.master_api.get('/api/booking/appointments/')
        self.assertEqual(master_list.status_code, status.HTTP_200_OK)
        master_results = master_list.data.get('results', master_list.data)
        self.assertEqual(len(master_results), 1)
        self.assertEqual(master_results[0]['master'], self.master_profile.id)
