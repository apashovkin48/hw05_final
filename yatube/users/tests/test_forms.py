import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserCreateFormTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Создания Post через валидную форму"""
        user_count = User.objects.count()
        User.objects.create_user(
            first_name='Имя',
            last_name='Фамилия',
            username='YatubeAdmin',
            email='yatubeadmin@ya.ru'
        )
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                pk=(user_count + 1),
                first_name='Имя',
                last_name='Фамилия',
                username='YatubeAdmin',
                email='yatubeadmin@ya.ru'
            ).exists()
        )
        self.assertIn
