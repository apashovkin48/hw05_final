from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_active = User.objects.create_user(username='user_active')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user_active)

    def test_pages_url_correct_template(self):
        """Проверка соответствия html шаблона страницам url"""
        template_urls = {
            '/auth/login/': {
                'template': 'users/login.html',
                'guest_client': True,
            },
            '/auth/signup/': {
                'template': 'users/signup.html',
                'guest_client': True,
            },
            '/auth/password_change/': {
                'template': 'users/password_change_form.html',
                'guest_client': False,
            },
            '/auth/password_change/done/': {
                'template': 'users/password_change_done.html',
                'guest_client': False,
            },
            '/auth/password_reset/': {
                'template': 'users/password_reset_form.html',
                'guest_client': True,
            },
            '/auth/password_reset/done/': {
                'template': 'users/password_reset_done.html',
                'guest_client': True,
            },
            '/auth/reset/Mw/66a-b758a7aa6f887e106fb2/': {
                'template': 'users/password_reset_confirm.html',
                'guest_client': True,
            },
            '/auth/reset/done/': {
                'template': 'users/password_reset_complete.html',
                'guest_client': True,
            },
            '/auth/logout/': {
                'template': 'users/logged_out.html',
                'guest_client': False,
            },
        }

        for url, template_info in template_urls.items():
            with self.subTest(address=url):
                client = self.authorized_client
                if template_info['guest_client']:
                    client = self.guest_client

                response = client.get(url)
                self.assertTemplateUsed(
                    response,
                    template_info['template']
                )
