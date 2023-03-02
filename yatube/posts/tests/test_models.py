from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    def test_model_post_metod_str(self):
        """У модели post используется метод __str__
           для предоставления инфомрации."""
        self.assertEqual(str(Post(text='Короткий пост')), 'Короткий пост')
        self.assertEqual(
            str(Post(text='str сокращает title до первых 15 строк')),
            'str сокращает t'
        )

    def test_model_group_metod_str(self):
        """У модели group используется метод __str__
        для предоставления информации."""
        self.assertEqual(str(Group(title='Новая группа')), 'Новая группа')

    def test_post_verbose_name(self):
        """При создании post, поле для поста называется "Текст поста."""
        self.assertEqual(
            Post._meta.get_field('text').verbose_name, 'Текст поста'
        )
