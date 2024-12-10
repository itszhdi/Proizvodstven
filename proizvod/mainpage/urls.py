from django.urls import path
from . import views
urlpatterns = [
    path('', views.show_main_page,name='main_page'),
    path('meme/', views.show_meme,name='meme'),
    path('set_city/', views.set_city, name='set_city')
]
