import json
import shutil
import tempfile
from io import BytesIO
from unittest import mock

import numpy as np
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from stl import mesh

from .models import Project

MEDIA = tempfile.mkdtemp()


def cube_stl(size=10.0):
    """Binary STL of a size×size×size mm cube (12 triangles)."""
    v = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                  [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], dtype=float) * size
    faces = [[0, 3, 1], [1, 3, 2], [0, 4, 7], [0, 7, 3], [4, 5, 6], [4, 6, 7],
             [5, 1, 2], [5, 2, 6], [2, 3, 6], [3, 7, 6], [0, 1, 5], [0, 5, 4]]
    cube = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        cube.vectors[i] = v[f]
    buf = BytesIO()
    cube.save('cube.stl', fh=buf)
    return SimpleUploadedFile('cube.stl', buf.getvalue(), content_type='model/stl')


@override_settings(MEDIA_ROOT=MEDIA)
class BaseCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user('alice', password='s3cret-pass-42')


class AuthTests(BaseCase):
    def test_login_redirects_to_projects(self):
        r = self.client.post(reverse('login'), {'username': 'alice', 'password': 's3cret-pass-42'})
        self.assertRedirects(r, reverse('projects'))

    def test_login_keeps_next(self):
        r = self.client.post(reverse('login') + '?next=/calculate/',
                             {'username': 'alice', 'password': 's3cret-pass-42'})
        self.assertRedirects(r, '/calculate/')

    def test_login_ignores_foreign_next(self):
        r = self.client.post(reverse('login') + '?next=https://evil.example/',
                             {'username': 'alice', 'password': 's3cret-pass-42'})
        self.assertRedirects(r, reverse('projects'))

    def test_register_creates_user_and_logs_in(self):
        r = self.client.post(reverse('register'), {'username': 'bob', 'password': 'Very-long-pass-9'})
        self.assertRedirects(r, reverse('projects'))
        self.assertTrue(User.objects.filter(username='bob').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='bob').id)

    def test_register_rejects_taken_username(self):
        r = self.client.post(reverse('register'), {'username': 'Alice', 'password': 'Very-long-pass-9'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'занято')
        self.assertEqual(User.objects.count(), 1)

    def test_projects_requires_login(self):
        r = self.client.get(reverse('projects'))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('login'), r['Location'])


class CalculateTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def post(self, url=None, **data):
        return self.client.post(url or reverse('calculate'), data)

    def test_upload_analyses_stl_and_prices(self):
        r = self.post(model_file=cube_stl(), density='1.25', price_per_kg='2000', markup='3')
        p = Project.objects.get()
        self.assertRedirects(r, reverse('calculate_with_id', args=[p.id]))
        self.assertEqual(p.status, 'ready')
        self.assertEqual(p.model_data['volume'], 1.0)           # 10 мм куб = 1 см³
        self.assertEqual(p.model_data['dimensions'], {'x': 10.0, 'y': 10.0, 'z': 10.0})
        self.assertEqual(p.model_data['polygons'], 12)
        # 1 см³ × 1.25 г/см³ × 20% заполнения = 0.25 г; 0.25 г × 2000/кг = 0.5; × 3 = 1.5 → 2
        self.assertEqual(p.model_data['weight'], 0.25)
        self.assertEqual(p.total_weight, 0.25)
        self.assertEqual(p.total_price, 2)

    def test_settings_are_saved(self):
        self.post(model_file=cube_stl(), technology='SLA', density='1.1', price_per_kg='3000', markup='2')
        p = Project.objects.get()
        self.assertEqual((p.technology, p.density, p.material_cost_per_kg, p.markup_coefficient),
                         ('SLA', 1.1, 3000.0, 2.0))

    def test_bad_numbers_do_not_crash(self):
        r = self.post(model_file=cube_stl(), density='abc', price_per_kg='', markup='-5')
        self.assertEqual(r.status_code, 302)

    def test_reupload_removes_old_file(self):
        self.post(model_file=cube_stl())
        p = Project.objects.get()
        old = p.model_file.path
        self.post(reverse('calculate_with_id', args=[p.id]), model_file=cube_stl(20))
        p.refresh_from_db()
        self.assertNotEqual(p.model_file.path, old)
        self.assertFalse(shutil.os.path.exists(old))
        self.assertEqual(p.model_data['volume'], 8.0)

    def test_broken_stl_marks_error(self):
        self.post(model_file=SimpleUploadedFile('bad.stl', b'not an stl'))
        self.assertEqual(Project.objects.get().status, 'error')

    def test_resave_keeps_title(self):
        self.post(model_file=cube_stl())
        p = Project.objects.get()
        p.title = 'Кронштейн'
        p.save()
        self.post(reverse('calculate_with_id', args=[p.id]), density='1.3')
        p.refresh_from_db()
        self.assertEqual(p.title, 'Кронштейн')

    def test_cannot_open_foreign_project(self):
        other = User.objects.create_user('eve', password='x-pass-123456')
        p = Project.objects.create(user=other, title='secret')
        self.assertEqual(self.client.get(reverse('calculate_with_id', args=[p.id])).status_code, 404)


@override_settings(GEMINI_API_KEY='test-key')
class AiTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            user=self.user, title='Кронштейн',
            model_data={'volume': 1.0, 'dimensions': {'x': 10, 'y': 20, 'z': 30}})
        self.url = reverse('generate_ai_text', args=[self.project.id])

    def fake_client(self, text):
        client = mock.Mock()
        client.models.generate_content.return_value = mock.Mock(text=text, parsed=None)
        return mock.patch('main.views._gemini_client', return_value=client)

    def test_anonymous_is_redirected(self):
        self.assertEqual(self.client.post(self.url).status_code, 302)

    def test_foreign_project_is_404(self):
        User.objects.create_user('eve', password='x-pass-123456')
        self.client.login(username='eve', password='x-pass-123456')
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_get_not_allowed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_success_saves_text(self):
        self.client.force_login(self.user)
        with self.fake_client(json.dumps({'description': 'Деталь', 'commercial': 'КП'})):
            r = self.client.post(self.url)
        self.assertEqual(r.json(), {'status': 'success', 'data': {'description': 'Деталь', 'commercial': 'КП'}})
        self.project.refresh_from_db()
        self.assertEqual(self.project.model_data['ai_description'], 'Деталь')
        self.assertEqual(self.project.model_data['ai_commercial'], 'КП')
        self.assertEqual(self.project.model_data['volume'], 1.0)

    def test_bad_ai_answer_is_500_json(self):
        self.client.force_login(self.user)
        with self.fake_client('not json'):
            r = self.client.post(self.url)
        self.assertEqual(r.status_code, 502)
        self.assertEqual(r.json()['status'], 'error')

    @override_settings(GEMINI_API_KEY='')
    def test_missing_key(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 503)
