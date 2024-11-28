from django.urls import path
from . import views
urlpatterns = [
    path('figuration/', views.figure_payment,name='figuration')
]
