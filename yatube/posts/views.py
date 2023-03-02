from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


from .models import Group, Post, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


def get_page_context(queryset, request):
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()
    context = {
        'title': title,
        'posts': posts,
    }
    context = get_page_context(Post.objects.all(), request)
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Запись сообщества'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.all()
    context = {
        'group': group,
        'posts': posts,
        'title': title,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    posts_count = posts.count()
    template = 'posts/profile.html'
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    context = {
        'author': author,
        'posts': posts,
        'posts_count': posts_count,
        'following': following
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    template = 'posts/post_detail.html'
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    tamplate = 'posts:post_detail'
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(tamplate, post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Подписки пользователя'
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts:profile'
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(template, author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts:profile'
    unfollowing = get_object_or_404(Follow, user=request.user, author=author)
    unfollowing.delete()
    return redirect(template, author)
