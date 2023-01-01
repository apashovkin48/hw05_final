from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from django import forms

from ..models import Post, Group, Following

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.reader = User.objects.create_user(username='reader')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='uniqueslug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    def setUp(self):
        self.reader_client = Client()
        self.reader_client.force_login(PostsPagesTests.reader)
        self.author_client = Client()
        self.author_client.force_login(PostsPagesTests.user)
        self.post = Post.objects.create(
            author=PostsPagesTests.user,
            text='Тестовый пост',
            group=PostsPagesTests.group,
            image=PostsPagesTests.uploaded,
        )
        cache.clear()

    def test_cache_index_template(self):
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            Post.objects.count(),
            len(response.context['page_obj'])
        )
        self.post.delete()
        self.assertNotEqual(
            Post.objects.count(),
            len(response.context['page_obj'])
        )
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            Post.objects.count(),
            len(response.context['page_obj'])
        )

    def test_follow_template(self):
        response = self.reader_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        Following.objects.create(
            user=PostsPagesTests.reader,
            author=PostsPagesTests.user
        )
        response = self.reader_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:follow_index'
            ): 'posts/follow.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'uniqueslug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'auth'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': 1}
            ): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_correct_form_context(self):
        """Проверка соответствия context формам создания и удаления поста"""
        url_form_fields = {
            reverse('posts:post_create'): {
                'text': forms.CharField,
                'group': forms.ModelChoiceField,
            },
            reverse('posts:post_edit', kwargs={'post_id': 1}): {
                'text': forms.CharField,
                'group': forms.ModelChoiceField,
            }
        }
        for reverse_name, form_fields in url_form_fields.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)

                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_post_correct_image_in_context(self):
        """Проверка что при выводе поста изображение передаётся в context"""
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'uniqueslug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
            reverse('posts:post_detail', kwargs={'post_id': 1}),
        ]

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertIsNotNone(response.context['post'].image)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='uniqueslug',
            description='Тестовое описание',
        )

        cls.POSTS_NUM: int = 14
        cls.POSTS_PAGE_NUM: int = 10
        for i in range(0, cls.POSTS_NUM):
            Post.objects.create(
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group,
                text=f'Пост{i+1}'
            )

        cls.paginator_info = {
            reverse(
                'posts:index'
            ): {
                'key_context': 'page_obj',
                'final_page': '?page=2'
            },
            reverse(
                'posts:group_list', kwargs={'slug': 'uniqueslug'}
            ): {
                'key_context': 'page_obj',
                'final_page': '?page=2'
            },
            reverse(
                'posts:profile', kwargs={'username': 'auth'}
            ): {
                'key_context': 'page_obj',
                'final_page': '?page=2'
            },
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PaginatorViewsTest.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Проверка размерности paginator с полной первой страницей"""
        paginator_info = PaginatorViewsTest.paginator_info
        for reverse_name, page_info in paginator_info.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(
                    len(response.context[page_info['key_context']]),
                    PaginatorViewsTest.POSTS_PAGE_NUM
                )

    def test_second_page_contains_three_records(self):
        """Проверка размерности paginator с неполной второй страницей"""
        paginator_info = PaginatorViewsTest.paginator_info
        for reverse_name, page_info in paginator_info.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(
                    reverse_name + page_info['final_page']
                )
                self.assertEqual(
                    len(response.context[page_info['key_context']]),
                    (
                        PaginatorViewsTest.POSTS_NUM
                        - PaginatorViewsTest.POSTS_PAGE_NUM
                    )
                )

    def test_post_list_page_show_correct_context(self):
        """Проверяем содержание context для первого элемента"""
        paginator_info = PaginatorViewsTest.paginator_info
        for reverse_name, page_info in paginator_info.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                first_object = response.context[page_info['key_context']][0]
                self.assertEqual(first_object.author, PaginatorViewsTest.user)
                self.assertEqual(
                    first_object.text,
                    f'Пост{PaginatorViewsTest.POSTS_NUM}'
                )
                self.assertEqual(first_object.group, PaginatorViewsTest.group)

    def test_post_detail_correct_context(self):
        """Проверка получения context о деталях поста"""
        POST_ID: int = 12
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': POST_ID})
        )
        self.assertEqual(
            response.context['post'].author,
            PaginatorViewsTest.user
        )
        self.assertEqual(
            response.context['post'].text,
            f'Пост{POST_ID}'
        )
        self.assertEqual(
            response.context['post'].group,
            PaginatorViewsTest.group
        )
