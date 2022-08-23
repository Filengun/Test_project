from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, User


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TestCreateForm.user)

    def test_create_post_auth(self):
        """
        Валидная форма создаёт новую запись в базе данных,
        затем перенаправляет на страницу профиля.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'author': TestCreateForm.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        obj = Post.objects.get(id=1)
        text = obj.text
        author = obj.author
        self.assertEqual(str(text), 'Тестовый пост')
        self.assertEqual(str(author), 'auth')

    def test_create_guest_client(self):
        """Проверка создание записи неавторизованного юзера"""
        form_data = {
            'text': 'Тестовый пост',
            'author': TestCreateForm.user,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post_auth(self):
        """Изменение записи зарегестрировнным пользователем"""
        self.existing_post = Post.objects.create(
            text='Тестовый пост',
            author=TestCreateForm.user,)
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'author': TestCreateForm.user
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.existing_post.id}),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.existing_post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        obj = Post.objects.get(id=1)
        text = obj.text
        author = obj.author
        self.assertEqual(str(text), 'Тестовый пост 2')
        self.assertEqual(str(author), 'auth')

    def test_edit_post_guest_client(self):
        """Проверка изменения записи неавторизованного юзера"""
        self.existing_post = Post.objects.create(
            text='Тестовый пост',
            author=TestCreateForm.user,)
        form_data = {
            'text': 'Тестовый пост 2',
            'author': TestCreateForm.user
        }
        response = self.guest_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.existing_post.id}),
            data=form_data
        )
        self.assertRedirects(response, f'/auth/login/?next=/posts/{self.existing_post.id}/edit/')
