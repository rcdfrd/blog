# Create your views here.
from django.contrib.auth import logout


def logout_view(request):
    logout(request)
