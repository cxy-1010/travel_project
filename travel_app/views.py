from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm

# Create your views here.

def index(request):
    """
    旅游网站的首页视图
    """
    return render(request, 'index.html')


class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'欢迎回来，{form.get_user().username}！')
        return super().form_valid(form)


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功，已为您自动登录。')
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, '您已安全退出登录。')
    return redirect(reverse_lazy('index'))
