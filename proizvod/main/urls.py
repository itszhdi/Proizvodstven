from django.urls import path
from . import views
urlpatterns = [
    path('', views.open_mainpage,name='main_page')
]
