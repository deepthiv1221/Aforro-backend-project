from django.urls import path
from . import views

urlpatterns = [
    path('api/search/products/', views.search_products, name='search_products'),
    path('api/search/suggest/', views.autocomplete_products, name='autocomplete_products'),
]