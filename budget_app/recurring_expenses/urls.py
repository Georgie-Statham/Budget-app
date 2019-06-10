from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('scheduled', views.scheduled, name='scheduled'),
    path('recurring_form', views.recurring_form, name='recurring_form'),
    path('<int:pk>/delete', login_required(
        views.RecurringDelete.as_view()) , name='recurring_delete'),
]
