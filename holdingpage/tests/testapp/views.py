from django.http import HttpResponse

from holdingpage.decorators import allowed_view

def index(request):
    return HttpResponse('Normal page')

def decorated_view(request):
    return HttpResponse('Normal page')
decorated_view = allowed_view(decorated_view)

def not_decorated_view(request):
    return HttpResponse('Normal page')

def a_view(request):
    return HttpResponse('Normal page')

def another_view(request):
    return HttpResponse('Normal page')