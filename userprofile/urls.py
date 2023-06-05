from django.urls import path

from . import views

app_name = 'userprofile'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
]
