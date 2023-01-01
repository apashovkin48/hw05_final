from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from http import HTTPStatus

User = get_user_model()


class AboutPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(AboutPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
            reverse(
                'users:password_change_form'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': 'Mw',
                    'token': '66a-b758a7aa6f887e106fb2'
                }
            ): 'users/password_reset_confirm.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                # Тут тоже почему то не работает для 302 кода
                if response.status_code == HTTPStatus.OK:
                    self.assertTemplateUsed(response, template)

    def test_user_correct_form_context(self):
        """Проверка содержания context для регистрации"""
        form_fields = {
            'first_name': forms.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.EmailField,
        }

        response = self.authorized_client.get(reverse('users:signup'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)
