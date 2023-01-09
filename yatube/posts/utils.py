from django.core.paginator import Paginator, Page
from django.db.models.query import QuerySet
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.shortcuts import get_object_or_404
from .models import User, Follow

CNT_POSTS_IN_PAGE: int = 10


def get_page_obj(data_list: QuerySet, request: WSGIRequest) -> Page:
    paginator = Paginator(data_list, CNT_POSTS_IN_PAGE)
    return paginator.get_page(request.GET.get('page'))


def is_can_add_subscribe(user: SimpleLazyObject, author_name: str) -> bool:
    author = get_object_or_404(User, username=author_name)
    if (
        not Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        and user.username != author.username
    ):
        return True
    return False


def is_can_del_subscribe(user: SimpleLazyObject, author_name: str) -> bool:
    author = get_object_or_404(User, username=author_name)
    if (
        Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        and user.username != author.username
    ):
        return True
    return False
