from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import EmailVerificationCode, TravelBooking, UserProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='用户名',
        error_messages={'required': '请输入用户名。'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='密码',
        error_messages={'required': '请输入密码。'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码',
        }),
    )


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='密码',
        error_messages={'required': '请设置密码。'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请设置密码',
        }),
    )
    password2 = forms.CharField(
        label='确认密码',
        error_messages={'required': '请再次输入密码。'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请再次输入密码',
        }),
    )
    email = forms.EmailField(
        label='邮箱',
        required=True,
        error_messages={
            'required': '请输入邮箱地址。',
            'invalid': '请输入正确的邮箱地址，例如 user@example.com。',
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址',
        }),
    )
    email_code = forms.CharField(
        label='邮箱验证码',
        max_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '未配置邮箱时可留空',
            'maxlength': '6',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'email_code', 'password1', 'password2')
        labels = {'username': '用户名'}
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('这个邮箱已经被注册，请直接登录或更换邮箱。')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次输入的密码不一致，请重新输入。')
        return password2

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        code = (cleaned_data.get('email_code') or '').strip()
        if not email or not code:
            return cleaned_data

        verification = EmailVerificationCode.objects.filter(
            email=email,
            purpose='register',
            is_used=False,
        ).order_by('-created_at').first()
        if not verification:
            self.add_error('email_code', '请先获取邮箱验证码，或留空直接注册。')
            return cleaned_data
        if verification.code != code:
            self.add_error('email_code', '邮箱验证码不正确。')
            return cleaned_data
        if verification.expires_at < timezone.now():
            self.add_error('email_code', '邮箱验证码已过期，请重新获取。')
            return cleaned_data
        self._email_verification = verification
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            verification = getattr(self, '_email_verification', None)
            if verification:
                verification.is_used = True
                verification.save(update_fields=['is_used'])
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label='邮箱',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址',
        }),
    )

    class Meta:
        model = UserProfile
        fields = ('email', 'phone', 'avatar')
        labels = {
            'phone': '手机号',
            'avatar': '头像',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入手机号',
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        exists = User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists()
        if exists:
            raise forms.ValidationError('这个邮箱已经被其他账号使用，请更换邮箱。')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('手机号只能包含数字、空格、+ 或 -。')
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError('头像文件不能超过 2MB。')
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save(update_fields=['email'])
            profile.save()
        return profile


class TravelBookingForm(forms.ModelForm):
    class Meta:
        model = TravelBooking
        fields = ('travelers', 'start_date', 'contact_phone', 'note')
        labels = {
            'travelers': '出行人数',
            'start_date': '出发日期',
            'contact_phone': '联系电话',
            'note': '备注',
        }
        widgets = {
            'travelers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入联系电话',
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '可填写特殊需求，例如房型、饮食偏好等',
            }),
        }

    def clean_travelers(self):
        travelers = self.cleaned_data.get('travelers') or 1
        if travelers < 1:
            raise forms.ValidationError('出行人数不能少于 1 人。')
        if travelers > 20:
            raise forms.ValidationError('线上预订最多支持 20 人，如需团队出行请联系客服。')
        return travelers
