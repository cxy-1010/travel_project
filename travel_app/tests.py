from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
