from django.urls import path
from . import views

app_name = 'adoptions'

urlpatterns = [
    path('', views.AdoptionCreateView.as_view(), name='adoption-create'),
    path('requests/', views.AdoptionRequestsView.as_view(), name='adoption-requests'),
]