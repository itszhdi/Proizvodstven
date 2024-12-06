from django.urls import path
from . import views
urlpatterns = [
    path('map/', views.figure_map,name='map'),
    path('astana/', views.figure_astana_map,name='astana'),
    path('almaty/', views.figure_almaty_map,name='almaty')
]
