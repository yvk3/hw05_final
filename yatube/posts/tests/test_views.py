from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('auth')
        cls.group = Group.objects.create(
            slug='slug',
            description='Описание новой группы',
        )
        cls.post = Post.objects.create(
            text='Текст нового поста',
            author=cls.user,
            group=cls.group,
        )
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'slug'},
            )
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    def test_forms_show_correct(self):
        """Создаётся форма для написания поста."""
        context = {
            reverse('posts:create'),
            reverse('posts:edit', kwargs={'post_id': self.post.id, }),
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)

    def test_post_context_group_list_template(self):
        """На странице группы отображаются посты данной группы."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.check_post_info(response.context['page_obj'][0])

    def test_posts_contaxt_profile_template(self):
        """На странице profile.html представлена информация
           об авторе постов."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.user)
        self.check_post_info(response.context['page_obj'][0])

    def test_posts_context_detail_template(self):
        """На странице post_detail.html представлена инфомрация о группе
           к которой относится пост и авторе поста ."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        self.check_post_info(response.context['post'])


class FollowTest(TestCase):
    """Тестируем подписчиков."""
    def setUp(self):
        self.author = User.objects.create_user(username='auth')
        self.user = User.objects.create_user(username='not_auth')
        self.not_follower = User.objects.create_user(
            username='not_follower'
        )
        self.post = Post.objects.create(
            text='Текст поста', author=self.author
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.not_follower)

    def test_follow_for_authorized_user(self):
        """Авторизованный пользователь может подписаться на автора."""
        follow_count = Follow.objects.filter(
            user=self.user, author=self.author
        ).count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.author.username,)))
        get_follow = Follow.objects.filter(user=self.user, author=self.author)
        self.assertEqual(get_follow.count(), follow_count + 1)

    def test_unfollow_for_authorized_user(self):
        """Авторизованный пользователь может отписаться от автора."""
        Follow.objects.create(user=self.user, author=self.author)
        follow_count = Follow.objects.filter(
            user=self.user, author=self.author
        ).count()
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.author.username,)))
        get_follow = Follow.objects.filter(user=self.user, author=self.author)
        self.assertEqual(get_follow.count(), follow_count - 1)

    def test_following_for_not_authorized_user(self):
        """Не авторизованвый пользователь не может подписаться на автора."""
        response = self.client.get(
            reverse('posts:profile_follow', args=(self.author.username,))
        )
        login_url = reverse('users:login')
        url = reverse('posts:profile_follow', args=(self.author.username,))
        self.assertRedirects(response, f'{login_url}?next={url}')

    def test_post_visibility_for_follower(self):
        """Проверяем видит ли подписчик посты автора."""
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.context['page_obj'][0], self.post)

    def test_not_following_to_myself(self):
        """Нельзя подписаться самому на себя."""
        follow_count = Follow.objects.filter(
            user=self.user, author=self.user
        ).count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user.username,)))
        get_follow = Follow.objects.filter(user=self.user, author=self.user)
        self.assertEqual(get_follow.count(), follow_count)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            slug='slug',
        )
        for i in range(13):
            Post.objects.create(
                text=f'Пост #{i}',
                author=cls.user,
                group=cls.group
            )
        cache.clear()

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Пагинации на страницах, на первой странице 10 постов,
           на второй странице 3 поста."""
        posts_on_first_page = 10
        posts_on_second_page = 3
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_ in url_pages:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(
                    len(self.unauthorized_client.get
                        (reverse_).context.get('page_obj')),
                    posts_on_first_page
                )
                self.assertEqual(
                    len(self.unauthorized_client.get(reverse_ + '?page=2').
                        context.get('page_obj')
                        ),
                    posts_on_second_page
                )
