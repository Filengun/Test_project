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
        self.authorized_client = Client()
        self.authorized_client.force_login(TestCreateForm.user)

    def test_create_post(self):
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
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                author=TestCreateForm.user
            ).exists()
        )

    def test_edit_post(self):
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
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост 2',
                author=TestCreateForm.user,
            )
        )
