from django.urls import path
from . import views
urlpatterns = [
    path('event/<int:event_id>/', views.open_event_page,name='event'),
    path('buy/<int:ticket_id>/', views.buy_ticket,name='buy'),
    path('redirect/<str:site>/<int:event_id>/', views.redirect_to_site, name='redirect_to_site'),
    path('search/', views.search_event, name='search'),
    path('process_order/<int:event_id>/', views.process_order, name='process_order'),
    path('check-auth/', views.check_auth, name='check_auth')
]
