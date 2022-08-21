from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostsPages(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group = cls.group,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_template(self):
        teplate_pages = {
            'posts/index.html': reverse('posts:first'),
            'posts/group_list.html': (
                reverse('posts:second', kwargs={'slug':'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username':'auth'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id':'1'})
            ),
            'posts/create_post.html': (reverse('posts:post_create')),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id':'1'})
            )
        }
        for template, names in teplate_pages.items():
            with self.subTest(names=names):
                response = self.authorized_client.get(names)
                self.assertTemplateUsed(response, template)
        
    def test_index_context(self):
        response = self.authorized_client.get(reverse('posts:first'))
        first_object = response.context['page_obj'][0]
        self.check_post_context(first_object)

    def test_group_context(self):
        response = self.authorized_client.get(reverse(
            'posts:second', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        self.check_post_context(first_object)

    def test_profile_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        first_object = response.context['page_obj'][0]
        self.check_post_context(first_object)

    def test_post_detail(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        first_object = response.context['post']
        self.check_post_context(first_object)

    def test_post_create(self):
        response =  self.authorized_client.get(reverse(
            'posts:post_create'))
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for parameter_1, parameter_2 in form.items():
            with self.subTest(parameter_1=parameter_1):
                form_field = response.context['form'].fields[parameter_1]
                self.assertIsInstance(form_field, parameter_2)

    def test_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for parameter_1, parameter_2 in form.items():
            with self.subTest(parameter_1=parameter_1):
                form_field = response.context.get('form').fields.get(parameter_1)
                self.assertIsInstance(form_field, parameter_2)

    def check_post_context(self, post):
        self.assertEqual(post.id, 1)
        self.assertEqual(str(post.author), 'auth')
        self.assertEqual(str(post.text), 'Тестовый пост')
        self.assertEqual(post.group, PostsPages.group)

    def test_post_is_not_in_group(self):
        self.second_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        response = self.authorized_client.get(reverse(
            'posts:second', kwargs={'slug': 'test-slug-2'}))
        self.assertEqual(
            response.context['group'].slug, self.second_group.slug)
        self.assertEqual(response.context['page_obj'].paginator.count, 0)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for _ in range(14):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTest.user)

    def test_paginator_one_list(self):
        template_pages_name = {
            reverse('posts:first'): 'page_obj',
            reverse('posts:second', kwargs={
                'slug': 'test-slug'}): 'page_obj',
        }
        for reverse_name, context in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context[context]), 10)

    def test_paginator_second_list(self):
        template_pages_name = {
            reverse('posts:first'): 'page_obj',
            reverse('posts:second', kwargs={
                'slug': 'test-slug'}): 'page_obj',
            reverse('posts:profile', kwargs={
                'username': 'auth'}): 'page_obj',
        }
        for reverse_name, context in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context[context]), 4)