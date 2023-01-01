from django.core.paginator import Paginator


def get_page_obj(data_list, request, cnt_posts_in_page=10):
    paginator = Paginator(data_list, cnt_posts_in_page)
    return paginator.get_page(request.GET.get('page'))
