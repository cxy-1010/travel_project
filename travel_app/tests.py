from datetime import timedelta
from threading import Event, Thread
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import EmailVerificationCode, Guide, GuideComment, SavedRoute, UserProfile


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

    def test_save_route_requires_login(self):
        response = self.client.post(
            reverse('save_route'),
            data='{"title":"杭州路线","destination":"杭州","content":"第1天 西湖"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(SavedRoute.objects.exists())

    def test_saved_route_shows_on_profile(self):
        user = User.objects.create_user(username='route_user', password='SafePass12345')
        self.client.login(username='route_user', password='SafePass12345')

        response = self.client.post(
            reverse('save_route'),
            data='{"title":"杭州路线","destination":"杭州","days":"3","people":"2","content":"第1天 西湖"}',
            content_type='application/json',
        )
        profile_response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(SavedRoute.objects.filter(user=user, title='杭州路线').exists())
        self.assertContains(profile_response, '杭州路线')
        self.assertContains(profile_response, '路线')

    def test_guide_comment_shows_on_profile(self):
        user = User.objects.create_user(username='comment_user', password='SafePass12345')
        guide = Guide.objects.create(
            user=user,
            title='上海周末攻略',
            destination='上海',
            content='外滩和武康路',
        )
        GuideComment.objects.create(
            user=user,
            guide=guide,
            title='回复：上海周末攻略',
            destination='上海',
            content='这个路线很适合两天游。',
        )
        self.client.login(username='comment_user', password='SafePass12345')

        response = self.client.get(reverse('profile'))

        self.assertContains(response, '评论')
        self.assertContains(response, '这个路线很适合两天游。')


@override_settings(
    EMAIL_HOST_USER='sender@qq.com',
    EMAIL_HOST_PASSWORD='qq-auth-code',
    DEFAULT_FROM_EMAIL='sender@qq.com',
)
class EmailVerificationCodeTests(TestCase):
    endpoint = 'send_email_code'

    @patch('travel_app.views.send_mail', return_value=1)
    def test_send_email_code_saves_code_and_returns_cooldown(self, send_mail_mock):
        response = self.client.post(
            reverse(self.endpoint),
            {'email': 'traveler@example.com'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['retry_after'], 60)
        verification = EmailVerificationCode.objects.get(email='traveler@example.com')
        self.assertRegex(verification.code, r'^\d{6}$')
        self.assertAlmostEqual(
            (verification.expires_at - verification.created_at).total_seconds(),
            600,
            delta=0.1,
        )
        send_mail_mock.assert_called_once()

    @patch('travel_app.views.send_mail')
    def test_send_email_code_returns_remaining_cooldown_without_sending(self, send_mail_mock):
        EmailVerificationCode.objects.create(
            email='traveler@example.com',
            code='123456',
            purpose='register',
            expires_at=EmailVerificationCode.default_expires_at(),
        )

        response = self.client.post(
            reverse(self.endpoint),
            {'email': 'traveler@example.com'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 429)
        self.assertGreaterEqual(response.json()['retry_after'], 59)
        self.assertEqual(response['Retry-After'], str(response.json()['retry_after']))
        send_mail_mock.assert_not_called()

    @patch('travel_app.views.send_mail', return_value=1)
    def test_send_email_code_allows_retry_after_sixty_seconds(self, send_mail_mock):
        verification = EmailVerificationCode.objects.create(
            email='traveler@example.com',
            code='123456',
            purpose='register',
            expires_at=EmailVerificationCode.default_expires_at(),
        )
        EmailVerificationCode.objects.filter(pk=verification.pk).update(
            created_at=timezone.now() - timedelta(seconds=61),
        )

        response = self.client.post(
            reverse(self.endpoint),
            {'email': 'traveler@example.com'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailVerificationCode.objects.filter(email='traveler@example.com').count(), 2)
        verification.refresh_from_db()
        self.assertTrue(verification.is_used)
        self.assertEqual(
            EmailVerificationCode.objects.filter(email='traveler@example.com', is_used=False).count(),
            1,
        )
        send_mail_mock.assert_called_once()

    @patch('travel_app.views.send_mail', side_effect=TimeoutError)
    def test_send_email_code_timeout_returns_quick_failure_without_stale_code(self, send_mail_mock):
        response = self.client.post(
            reverse(self.endpoint),
            {'email': 'traveler@example.com'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['error'], '验证码发送失败，请稍后重试')
        self.assertFalse(EmailVerificationCode.objects.filter(email='traveler@example.com').exists())
        send_mail_mock.assert_called_once()

    def test_database_allows_only_one_unused_code_per_email_and_purpose(self):
        EmailVerificationCode.objects.create(
            email='traveler@example.com',
            code='123456',
            purpose='register',
            expires_at=EmailVerificationCode.default_expires_at(),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                EmailVerificationCode.objects.create(
                    email='traveler@example.com',
                    code='654321',
                    purpose='register',
                    expires_at=EmailVerificationCode.default_expires_at(),
                )


@override_settings(
    EMAIL_HOST_USER='sender@qq.com',
    EMAIL_HOST_PASSWORD='qq-auth-code',
    DEFAULT_FROM_EMAIL='sender@qq.com',
)
class EmailVerificationConcurrencyTests(TransactionTestCase):
    @patch('travel_app.views.send_mail')
    def test_concurrent_request_does_not_send_a_second_code(self, send_mail_mock):
        send_started = Event()
        release_send = Event()
        first_responses = []
        first_errors = []

        def slow_send(*args, **kwargs):
            send_started.set()
            release_send.wait(timeout=5)
            return 1

        def send_first_request():
            try:
                first_responses.append(Client().post(
                    reverse('send_email_code'),
                    {'email': 'traveler@example.com'},
                    content_type='application/json',
                ))
            except Exception as exc:
                first_errors.append(exc)

        send_mail_mock.side_effect = slow_send
        first_thread = Thread(target=send_first_request)
        first_thread.start()
        self.assertTrue(send_started.wait(timeout=5))

        try:
            second_response = Client().post(
                reverse('send_email_code'),
                {'email': 'traveler@example.com'},
                content_type='application/json',
            )
        finally:
            release_send.set()
            first_thread.join(timeout=5)

        self.assertFalse(first_thread.is_alive())
        self.assertFalse(first_errors)
        self.assertEqual(first_responses[0].status_code, 200)
        self.assertEqual(second_response.status_code, 429)
        self.assertEqual(send_mail_mock.call_count, 1)
        self.assertEqual(
            EmailVerificationCode.objects.filter(
                email='traveler@example.com',
                purpose='register',
                is_used=False,
            ).count(),
            1,
        )
