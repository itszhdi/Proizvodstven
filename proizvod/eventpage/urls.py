from django.urls import path
from . import views
urlpatterns = [
    path('event/<int:event_id>/', views.open_event_page,name='event'),
    path('buy/<int:event_id>/', views.buy_ticket,name='buy')
]
