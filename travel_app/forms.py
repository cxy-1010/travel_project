from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


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


class RegisterForm(UserCreationForm):
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
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请设置密码',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请再次输入密码',
        })
        self.fields['password1'].error_messages.update({
            'required': '请设置密码。',
        })
        self.fields['password2'].error_messages.update({
            'required': '请再次输入密码。',
        })

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
