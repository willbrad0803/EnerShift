from decimal import Decimal
from io import BytesIO

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import MeterReading, Site, UserProfile


def make_user(username='alice', email='alice@example.com', password='testpass123'):
    return User.objects.create_user(username=username, email=email, password=password)


class UserProfileSignalTests(TestCase):
    """A UserProfile should be created automatically for every new User."""

    def test_profile_created_on_user_creation(self):
        user = make_user()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.role, 'CUSTOMER')

    def test_profile_not_duplicated_on_save(self):
        user = make_user()
        user.first_name = 'Alice'
        user.save()
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)


class EmailAuthenticationBackendTests(TestCase):
    """
    Regression test for the AUTHENTICATION_BACKENDS fix: ACCOUNT_LOGIN_METHODS
    is set to {'email'}, so authenticating with an email address must work.
    """

    def test_can_authenticate_with_email(self):
        make_user(username='bob', email='bob@example.com', password='testpass123')
        user = authenticate(username='bob@example.com', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'bob@example.com')

    def test_wrong_password_fails(self):
        make_user(username='carol', email='carol@example.com', password='testpass123')
        user = authenticate(username='carol@example.com', password='wrong-password')
        self.assertIsNone(user)


class SiteModelTests(TestCase):
    def test_site_belongs_to_user(self):
        user = make_user()
        site = Site.objects.create(user=user, name='Warehouse 1', postcode='M1 1AE')
        self.assertEqual(site.user, user)
        self.assertEqual(str(site), 'Warehouse 1 (M1 1AE)')

    def test_duplicate_site_name_per_user_rejected(self):
        user = make_user()
        Site.objects.create(user=user, name='Warehouse 1', postcode='M1 1AE')
        with self.assertRaises(Exception):
            Site.objects.create(user=user, name='Warehouse 1', postcode='M2 2BF')


class DashboardViewAccessTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_dashboard_lists_only_own_sites(self):
        owner = make_user(username='owner', email='owner@example.com')
        other = make_user(username='other', email='other@example.com')
        Site.objects.create(user=owner, name='Owner Site', postcode='M1 1AE')
        Site.objects.create(user=other, name='Other Site', postcode='M2 2BF')

        self.client.force_login(owner)
        response = self.client.get(reverse('dashboard_home'))

        self.assertEqual(response.status_code, 200)
        site_names = [s.name for s in response.context['sites']]
        self.assertIn('Owner Site', site_names)
        self.assertNotIn('Other Site', site_names)


class UploadMeterDataTests(TestCase):
    """
    Covers the bug fix in upload_meter_data: valid rows import, malformed
    rows are skipped (not silently swallowed with no feedback, and not a
    hard 500), and the user always ends up back on a real page.
    """

    def setUp(self):
        self.user = make_user()
        self.site = Site.objects.create(user=self.user, name='Site A', postcode='M1 1AE')
        self.client.force_login(self.user)

    def _upload(self, csv_content):
        csv_file = SimpleUploadedFile(
            'readings.csv', csv_content.encode('utf-8'), content_type='text/csv'
        )
        return self.client.post(
            reverse('upload_meter_data'),
            {'site_id': self.site.id, 'csv_file': csv_file},
        )

    def test_valid_rows_are_imported(self):
        csv_content = (
            'timestamp,consumption_kwh,export_kwh\n'
            '2026-01-01T00:00:00Z,1.5,0\n'
            '2026-01-01T00:30:00Z,2.0,0\n'
        )
        response = self._upload(csv_content)

        self.assertRedirects(response, reverse('dashboard_home'))
        self.assertEqual(MeterReading.objects.filter(site=self.site).count(), 2)

    def test_readings_stored_as_timezone_aware(self):
        csv_content = 'timestamp,consumption_kwh,export_kwh\n2026-01-01T00:00:00Z,1.5,0\n'
        self._upload(csv_content)

        reading = MeterReading.objects.get(site=self.site)
        self.assertTrue(reading.timestamp.tzinfo is not None)

    def test_malformed_row_is_skipped_not_fatal(self):
        csv_content = (
            'timestamp,consumption_kwh,export_kwh\n'
            'not-a-timestamp,1.5,0\n'
            '2026-01-01T00:30:00Z,2.0,0\n'
        )
        response = self._upload(csv_content)

        # Good row still imported; the whole request must not 500.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MeterReading.objects.filter(site=self.site).count(), 1)

    def test_cannot_upload_to_another_users_site(self):
        other_user = make_user(username='mallory', email='mallory@example.com')
        other_site = Site.objects.create(user=other_user, name='Not Yours', postcode='M3 3CD')

        csv_file = SimpleUploadedFile(
            'readings.csv',
            b'timestamp,consumption_kwh,export_kwh\n2026-01-01T00:00:00Z,1.5,0\n',
            content_type='text/csv',
        )
        response = self.client.post(
            reverse('upload_meter_data'),
            {'site_id': other_site.id, 'csv_file': csv_file},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(MeterReading.objects.filter(site=other_site).count(), 0)

    def test_completely_invalid_file_does_not_500(self):
        """A non-CSV upload should redirect with an error, never crash the request."""
        bogus_file = SimpleUploadedFile(
            'not_a_csv.bin', BytesIO(b'\x00\x01\x02\x03').read(), content_type='application/octet-stream'
        )
        response = self.client.post(
            reverse('upload_meter_data'),
            {'site_id': self.site.id, 'csv_file': bogus_file},
        )
        self.assertNotEqual(response.status_code, 500)
