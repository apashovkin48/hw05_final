from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from http import HTTPStatus
from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_active = User.objects.create_user(username='user_active')
        cls.group = Group.objects.create(
            title='Test Group',
            slug='uniqueslug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user_active,
            text=(
                'В этом посте что то находится, '
                'возможно то, что вы сейчас читаете'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user_active)
        cache.clear()
        self.template_urls = {
            '/': {
                'authorization': False,
                'template': 'posts/index.html',
                'redirect': None
            },
            '/group/uniqueslug/': {
                'authorization': False,
                'template': 'posts/group_list.html',
                'redirect': None
            },
            '/profile/user_active/': {
                'authorization': False,
                'template': 'posts/profile.html',
                'redirect': None
            },
            '/posts/1/': {
                'authorization': False,
                'template': 'posts/post_detail.html',
                'redirect': None
            },
            '/posts/1/edit/': {
                'authorization': True,
                'template': 'posts/create_post.html',
                'redirect': {
                    'guest': '/auth/login/?next=/posts/1/edit/',
                    'authorized': '/posts/1/'
                }
            },
            '/create/': {
                'authorization': True,
                'template': 'posts/create_post.html',
                'redirect': {
                    'guest': '/auth/login/?next=/create/',
                    'authorized': '/profile/user_active/'
                }
            },
            '/follow/': {
                'authorization': True,
                'template': 'posts/follow.html',
                'redirect': None,
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

    def test_pages_redirect_guest(self):
        """Проверка redirect для гостя"""
        for url, url_info in self.template_urls.items():
            with self.subTest(address=url):
                if (url_info['redirect'] is not None):
                    response = self.guest_client.get(url, follow=True)
                    self.assertRedirects(
                        response,
                        url_info['redirect']['guest']
                    )
