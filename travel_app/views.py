from django.shortcuts import render

# Create your views here.

def index(request):
    """
    旅游网站的首页视图
    """
    return render(request, 'index.html')