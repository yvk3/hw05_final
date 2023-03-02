import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageExistTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Группа для проверки',
            slug='slug',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_post_with_image_exist(self):
        self.assertTrue(Post.objects.filter(image=self.post.image.name))

    def test_index_show_correct_image_in_context(self):
        """В Шаблоне index картинка передается в словаре context"""
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        test_object = response.context['page_obj'][0]
        post_image = test_object.image
        self.assertEqual(post_image, self.post.image.name)

    def test_post_detail_image_exist(self):
        """В шаблоне post_detail картинка передается в словаре context"""
        response = self.author_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        test_object = response.context['post']
        post_image = test_object.image
        self.assertEqual(post_image, self.post.image.name)

    def test_group_and_profile_image_exist(self):
        """В шаблонах group и profile картинка передается в словаре context"""
        templates_pages_name = {
            'posts:group_list': self.group.slug,
            'posts:profile': self.user.username,
        }
        for names, args in templates_pages_name.items():
            with self.subTest(names=names):
                response = self.author_client.get(reverse(names, args=[args]))
                test_object = response.context['page_obj'][0]
                post_image = test_object.image
                self.assertEqual(post_image, self.post.image.name)
