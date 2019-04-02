from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('overview', views.overview, name='overview'),
    path('payback_form', views.payback_form, name='payback_form'),
    path('<int:pk>/update', login_required(
        views.PaybackUpdate.as_view()), name='payback_update'),
    path('<int:pk>/delete', login_required(
        views.PaybackDelete.as_view()) , name='payback_delete'),
]
