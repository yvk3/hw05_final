from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        db_index=True
    )
    description = models.TextField()

    class Meta:
        verbose_name = 'Группа статей'
        verbose_name_plural = 'Группы статей'
        ordering = ('-title',)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор статьи"
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name="Группа",
        help_text="Выберите название группы"
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя автора',
        help_text='Укажите автора',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Укажите текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )
    active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Укажите подписчика',
        help_text='Подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Укажите на кого подписываемся',
        help_text='Автор поста',
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follows',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}'
