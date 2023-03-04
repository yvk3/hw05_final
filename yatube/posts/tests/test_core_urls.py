from http import HTTPStatus

from django.test import Client, TestCase


class CoreUrlsTests(TestCase):
    """Проверка корректной работы страницы 404 и её шаблона."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_404_exists_at_desired_location(self):
        """При запросе несуществующей стрнаицы будет выдано сообщение 404."""
        self.assertEqual(
            Client().get('page').status_code,
            HTTPStatus.NOT_FOUND,
            'Error 404 page'
        )

    def test_404_uses_correct_template(self):
        """При запросе несуществующей стрнаицы будет загружен шаблон
        с сообщением от ошибке 404.."""
        self.assertTemplateUsed(
            Client().get('page'),
            'core/404.html',
            'Error 404 temp.'
        )
