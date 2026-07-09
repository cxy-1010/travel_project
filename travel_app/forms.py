from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import UserProfile


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

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        error_messages = {
            'username': {
                'required': '请输入用户名。',
                'unique': '这个用户名已经被注册，请换一个。',
                'invalid': '用户名只能包含字母、数字和 @/./+/-/_ 字符。',
            },
        }
        labels = {
            'username': '用户名',
            'password1': '密码',
            'password2': '确认密码',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
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
        error_messages = {
            'avatar': {
                'invalid_image': '请上传有效的图片文件。',
            },
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
