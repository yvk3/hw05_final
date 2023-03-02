from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            'post_author',
        )
        cls.group = Group.objects.create(
            title='Новая группа',
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_authorized_user_create_post(self):
        """Авторизированный пользователь создаёт пост."""
        old_post_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        assert Post.objects.count() == old_post_count + 1
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])

    def test_authorized_user_edit_post(self):
        """Авторизированный пользователь редактирует ранее созданный
        и сохранённый пост."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
        }
        response = self.authorized_user.post(
            reverse(
                'posts:edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == self.post_author)

    def test_nonauthorized_user_create_post(self):
        """Не авторизированный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Поле для ввода текста поста',
        }
        response = self.guest_user.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Новая группа',
            slug='slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст gjcnf',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Текст комментария',
            post=cls.post
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_add_comment(self):
        """Авторезированный пользователь создаётся комментарий к посту."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.post.text
        }
        response = self.author_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[self.post.id]))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        last_object = Comment.objects.order_by('-id').first()
        self.assertEqual(form_data['text'], last_object.text)
        self.assertEqual(self.comment.post.id, last_object.post.id)
