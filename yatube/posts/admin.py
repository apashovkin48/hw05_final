from django.contrib import admin
from .models import Post, Group, Comment, Following


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'post',
        'author',
        'text',
        'created',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class FollowingAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    empty_value_display = '-пусто-'


# При регистрации модели Post источником конфигурации для неё назначаем
# класс PostAdmin
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Following, FollowingAdmin)
admin.site.register(Group)
