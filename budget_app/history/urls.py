from django.urls import path, re_path
from . import views

urlpatterns = [
    path('current_month', views.current_month, name='current_month'),
    path('current_month/<int:pk>/update', views.ExpenseUpdate.as_view(), name='expense_update'),
    path('current_month/<int:pk>/delete', views.ExpenseDelete.as_view(), name='expense_delete'),
    path('previous_month/<month>_<int:year>', views.previous_month, name='previous_month'),
    path('previous_month/<int:pk>/update', views.PreviousExpenseUpdate.as_view(), name='expense_update'),
    path('previous_month/<int:pk>/delete', views.PreviousExpenseDelete.as_view(), name='expense_delete'),
]
