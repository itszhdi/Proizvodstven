from django.urls import path
from . import views
urlpatterns = [
    path('user/', views.render_info,name='user'),
    path('log/', views.logout_user, name='log')
]
