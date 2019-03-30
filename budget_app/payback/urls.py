from django.urls import path
from . import views

urlpatterns = [
    path('overview', views.overview, name='overview'),
    path('payback_form', views.payback_form, name='payback_form')
]
