from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomerCreateView.as_view(), name='customer-create'),
]