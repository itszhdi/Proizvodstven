from django.urls import path
from . import views
urlpatterns = [
    path('event/', views.open_event_page,name='event'),
    path('buy/', views.buy_ticket,name='buy')
]
