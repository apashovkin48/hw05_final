from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок группы",
        help_text='Заполните заголовок группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug страницы',
        help_text='Заполните slug группы'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Заполните описание группы'
    )

    def __str__(self):
        return self.title


class Post(BaseModel):
    text = models.TextField(
        verbose_name="Текст статьи",
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор поста, известен при аутентификации пользователя'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name="Группа",
        help_text=(
            'Выберите группу поста, '
            'если он подходит по смыслу одной из имеющихся'
        )
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(BaseModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Комментарий оставляется под постами'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор поста, известен при аутентификации пользователя'
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text='Введите текст комментария'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
        help_text='Текущий поьзователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Автор на которого ты хочешь подписаться'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique subscribe'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.author.username}"
