from django.urls import path
from . import views

urlpatterns = [
    path('', views.PetListCreateView.as_view(), name='pet-list-create'),
]