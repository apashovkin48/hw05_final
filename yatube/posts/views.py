from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import get_page_obj, is_can_add_subscribe, is_can_del_subscribe
from django.views.decorators.cache import cache_page


def belong_post_author(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        post_id = kwargs['post_id']
        if request.user == Post.objects.get(pk=post_id).author:
            return func(*args, **kwargs)
        else:
            return redirect('posts:post_detail', post_id)
    return wrapper


@cache_page(60 * 20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = get_page_obj(post_list, request)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group', 'author')
    page_obj = get_page_obj(post_list, request)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group', 'author')
    page_obj = get_page_obj(post_list, request)

    context = {
        'page_obj': page_obj,
        'author': author
    }
    if not request.user.is_anonymous:
        context['following'] = is_can_add_subscribe(request.user, username)
        context['unfollowing'] = is_can_del_subscribe(request.user, username)
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)

    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
@belong_post_author
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_obj(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if (is_can_add_subscribe(request.user, username)):
        Follow.objects.create(
            user=request.user,
            author=get_object_or_404(User, username=username)
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    if (is_can_del_subscribe(request.user, username)):
        Follow.objects.filter(
            user=request.user,
            author=get_object_or_404(User, username=username)
        ).delete()
    return redirect('posts:profile', username)
