from urllib import response
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)


    def test_na_status_noname(self):
        """Прогон страниц для неавторизованного."""
        temp_url = [
            '/',
            '/group/test-slug/',
            '/profile/Test_auth/',
            '/posts/1/'
        ]
        for i in temp_url:
            with self.subTest():
                response = self.guest_client.get(i)
                self.assertEqual(response.status_code, 200, "раз")

    
    def test_na_status_auth(self):
        """Создание поста."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200, "два")

    
    def test_edit(self):
        """Редактирование поста."""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200, "три")


    def test_no_post(self):
        """Несуществующая страница. Ошибка 404."""
        response = self.authorized_client.get('/posts/6/')
        self.assertEqual(response.status_code, 404, "четыре")