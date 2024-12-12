from django.urls import path
from . import views
urlpatterns = [
    path('user/', views.render_info,name='user'),
    path('log/', views.logout_user, name='log'),
    path('delete/', views.delete_user_info, name='delete'),
    path('add/', views.add_event, name='add'),
    path('mytickets/', views.show_list, name='mytickets'),
    path('ticket_search/', views.ticket_search, name='ticket_search')
]
