from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

        self.template_urls = {
            '/about/author/': {
                'authorization': False,
                'template': 'about/author.html',
                'redirect': None
            },
            '/about/tech/': {
                'authorization': False,
                'template': 'about/tech.html',
                'redirect': None
            }
        }

    def test_pages_url_status_code(self):
        """Проверка status code для url"""
        for url, url_info in self.template_urls.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                if url_info['authorization']:
                    response = self.authorized_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_url_correct_template(self):
        """Проверка соответствия html шаблона страницам url"""
        for url, url_info in self.template_urls.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                if url_info['authorization']:
                    response = self.authorized_client.get(url)

                self.assertTemplateUsed(
                    response,
                    url_info['template']
                )
