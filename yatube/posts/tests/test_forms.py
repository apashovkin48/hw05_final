import shutil
import tempfile

from ..models import Group, Post, Comment, Follow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostsCreateFormTests.user)
        self.reader_client = Client()
        self.reader_client.force_login(PostsCreateFormTests.reader)

    def test_create_post(self):
        """Создания Post через валидную форму"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': PostsCreateFormTests.group.pk
        }

        self.assertRedirects(
            self.guest_client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True
            ),
            '/auth/login/?next=/create/'
        )

        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                pk=(posts_count + 1),
                author=PostsCreateFormTests.user,
                text='Тестовый пост',
                group=PostsCreateFormTests.group
            ).exists()
        )

    def test_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'post': PostsCreateFormTests.post,
            'author': PostsCreateFormTests.user,
            'text': 'Интересно, но можно и лучше'
        }
        response = self.author_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostsCreateFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsCreateFormTests.post.id}
            )
        )

        self.assertEqual(Post.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                pk=(comment_count + 1),
                post=PostsCreateFormTests.post,
                author=PostsCreateFormTests.user,
                text='Интересно, но можно и лучше',
            ).exists()
        )

    def test_edit_post(self):
        """Изменение Post через валидную форму"""
        form_data = {
            'text': 'Новое содержание поста',
            'group': PostsCreateFormTests.group.pk
        }

        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsCreateFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsCreateFormTests.post.pk}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                pk=PostsCreateFormTests.post.pk,
                author=PostsCreateFormTests.user,
                text='Новое содержание поста',
                group=PostsCreateFormTests.group
            ).exists()
        )

    def test_create_post_with_image(self):
        """Создание поста с изображением"""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostsCreateFormTests.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': PostsCreateFormTests.group.pk,
            'image': uploaded,
        }
        self.assertRedirects(
            self.guest_client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True
            ),
            '/auth/login/?next=/create/'
        )
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                pk=(posts_count + 1),
                author=PostsCreateFormTests.user,
                text='Тестовый пост',
                group=PostsCreateFormTests.group
            ).exists()
        )

    def test_edit_post_with_image(self):
        """Добавление изображения в пост, где его не было"""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostsCreateFormTests.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новое содержание поста',
            'group': PostsCreateFormTests.group.pk,
            'image': uploaded,
        }
        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostsCreateFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsCreateFormTests.post.pk}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                pk=PostsCreateFormTests.post.pk,
                author=PostsCreateFormTests.user,
                text='Новое содержание поста',
                group=PostsCreateFormTests.group,
            ).exists()
        )

    def test_subscribe_and_unsubscribe_author(self):
        cnt_following = Follow.objects.count()
        response = self.reader_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostsCreateFormTests.user}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostsCreateFormTests.user}
            )
        )
        self.assertEqual(Follow.objects.count(), cnt_following + 1)

        response = self.reader_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostsCreateFormTests.user}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostsCreateFormTests.user}
            )
        )
        self.assertEqual(Follow.objects.count(), cnt_following)
