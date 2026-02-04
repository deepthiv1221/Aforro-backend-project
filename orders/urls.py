from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.create_order, name='create_order'),
]