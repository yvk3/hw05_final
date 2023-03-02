from http import HTTPStatus
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Новая группа',
            slug='slug',
            description='Описание новой группы',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текст нового поста',
        )
        cls.templates_url_names_public = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            'posts/profile.html':
            reverse('posts:profile', kwargs={'username': cls.author.username}),
        }
        cls.templates_url_names_private = {
            'posts/create_post.html': reverse('posts:create')
        }
        cls.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            'posts/profile.html':
            reverse('posts:profile', kwargs={'username': cls.author.username}),
            'posts/create_post.html': reverse('posts:create'),
        }
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.auth_user_client = Client()
        self.auth_user_client.force_login(self.auth_user)

    def test_urls_guest_user_not_private_template(self):
        """
        Не зарегистрированный пользователь может посмотреть только
        первую страница, при попытке перейти на другие
        страницы - предлагают зарегестрироваться.
        """
        for template, reverse_name in self.templates_url_names_private.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_can_write_and_edit_post(self):
        """Автор поста может создавать посты и редактировать их."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_no_authorized_user_can_look_post_not_edit(self):
        """Авторизованный пользователь может просматривать детали поста,
           но не может их редактировать."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                if reverse_name == reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.id},
                ):
                    response = self.author_user_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.auth_user_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """При вводе URL-адреса открывается шаблон прописанный в urls."""
        cache.clear()
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
