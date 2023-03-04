from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    def test_model_post_metod_str(self):
        """Краткость, сестра таланта(с).
        Навание поста должно быть до 15 символов."""
        self.assertEqual(str(Post(text='Короткий пост')), 'Короткий пост')
        self.assertEqual(
            str(Post(text='str сокращает title до первых 15 строк')),
            'str сокращает t'
        )

    def test_model_group_metod_str(self):
        self.assertEqual(str(Group(title='Новая группа')), 'Новая группа')

    def test_post_verbose_name(self):
        """Читаем подсказки"""
        self.assertEqual(
            Post._meta.get_field('text').verbose_name, 'Текст поста'
        )
