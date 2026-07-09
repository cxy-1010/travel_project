from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class AuthFlowTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'traveler',
            'email': 'traveler@example.com',
            'password1': 'SafePass12345',
            'password2': 'SafePass12345',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='traveler').exists())
        self.assertContains(response, 'traveler')

    def test_register_allows_simple_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'simple',
            'email': 'simple@example.com',
            'password1': '123',
            'password2': '123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='simple')
        self.assertTrue(user.check_password('123'))

    def test_login_and_logout_flow(self):
        User.objects.create_user(username='demo', password='SafePass12345')

        login_response = self.client.post(reverse('login'), {
            'username': 'demo',
            'password': 'SafePass12345',
        }, follow=True)
        self.assertContains(login_response, 'demo')

        logout_response = self.client.get(reverse('logout'), follow=True)
        self.assertContains(logout_response, '登录')

    def test_register_rejects_invalid_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'badmail',
            'email': 'not-an-email',
            'password1': 'SafePass12345',
            'password2': 'SafePass12345',
        })

        self.assertContains(response, '请输入正确的邮箱地址')
        self.assertFalse(User.objects.filter(username='badmail').exists())

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username='first',
            email='same@example.com',
            password='SafePass12345',
        )

        response = self.client.post(reverse('register'), {
            'username': 'second',
            'email': 'same@example.com',
            'password1': 'SafePass12345',
            'password2': 'SafePass12345',
        })

        self.assertContains(response, '这个邮箱已经被注册')
        self.assertFalse(User.objects.filter(username='second').exists())

    def test_password_is_stored_as_hash(self):
        self.client.post(reverse('register'), {
            'username': 'hashed',
            'email': 'hashed@example.com',
            'password1': 'SafePass12345',
            'password2': 'SafePass12345',
        })

        user = User.objects.get(username='hashed')
        self.assertNotEqual(user.password, 'SafePass12345')
        self.assertTrue(user.password.startswith('pbkdf2_'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_profile_page_can_update_email_and_phone(self):
        user = User.objects.create_user(
            username='profile_user',
            email='old@example.com',
            password='SafePass12345',
        )
        self.client.login(username='profile_user', password='SafePass12345')

        response = self.client.post(reverse('profile'), {
            'email': 'new@example.com',
            'phone': '138 0000 0000',
        }, follow=True)

        self.assertContains(response, '个人信息已更新')
        user.refresh_from_db()
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.profile.phone, '138 0000 0000')

    def test_profile_is_created_for_existing_user(self):
        user = User.objects.create_user(username='legacy', password='SafePass12345')
        self.assertFalse(UserProfile.objects.filter(user=user).exists())
        self.client.login(username='legacy', password='SafePass12345')

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_home_profile_link_and_profile_page_work_for_logged_in_legacy_user(self):
        user = User.objects.create_user(username='legacy_nav', password='1')
        self.assertFalse(UserProfile.objects.filter(user=user).exists())
        self.client.login(username='legacy_nav', password='1')

        home_response = self.client.get(reverse('index'))
        profile_response = self.client.get(reverse('profile'))

        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
