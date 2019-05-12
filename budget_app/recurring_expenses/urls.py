from django.urls import path
from . import views

urlpatterns = [
    path('scheduled/', views.scheduled, name='scheduled'),
    path('recurring_form/', views.recurring_form, name='recurring_form'),
]
