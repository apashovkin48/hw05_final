from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.reader = User.objects.create_user(username='reader')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.following = Follow.objects.create(
            user=cls.reader,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        # Напишите проверку тут
        post = PostModelTest.post
        group = PostModelTest.group
        following = PostModelTest.following
        self.assertEqual(post.__str__(), post.text[:15])
        self.assertEqual(group.__str__(), group.title)
        self.assertEqual(
            following.__str__(),
            f"{PostModelTest.reader} - {PostModelTest.user}"
        )

    def test_models_help_text(self):
        """Проверяем help text для моделей Post, Group и Following"""
        def check_help_text_fields(
            self,
            info_dict,
            model
        ) -> None:
            for field, help_text_value in info_dict.items():
                self.assertEqual(
                    model._meta.get_field(field).help_text, help_text_value
                )

        check_help_text_fields(
            self,
            {
                'text': 'Введите текст поста',
                'created': 'Дата создания, ставится автоматически',
                'author': (
                    'Автор поста, известен при '
                    'аутентификации пользователя'
                ),
                'group': (
                    'Выберите группу поста, если он подходит '
                    'по смыслу одной из имеющихся'
                )
            },
            PostModelTest.post
        )
        check_help_text_fields(
            self,
            {
                'title': 'Заполните заголовок группы',
                'slug': 'Заполните slug группы',
                'description': 'Заполните описание группы'
            },
            PostModelTest.group
        )
        check_help_text_fields(
            self,
            {
                'user': 'Текущий поьзователь',
                'author': 'Автор на которого ты хочешь подписаться'
            },
            PostModelTest.following
        )

    def test_models_verbose_name(self):
        """Проверяем verbose name для моделей Post и Group"""
        def check_verbose_name_fields(
            self,
            info_dict,
            model
        ) -> None:
            for field, help_text_value in info_dict.items():
                self.assertEqual(
                    model._meta.get_field(field).verbose_name, help_text_value
                )

        check_verbose_name_fields(
            self,
            {
                'text': 'Текст статьи',
                'created': 'Дата создания',
                'author': 'Автор',
                'group': 'Группа'
            },
            PostModelTest.post
        )
        check_verbose_name_fields(
            self,
            {
                'title': 'Заголовок группы',
                'slug': 'slug страницы',
                'description': 'Описание группы'
            },
            PostModelTest.group
        )
        check_verbose_name_fields(
            self,
            {
                'user': 'Пользователь',
                'author': 'Автор'
            },
            PostModelTest.following
        )
