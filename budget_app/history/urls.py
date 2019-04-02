from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('detailed_month/<month>_<int:year>', views.detailed_month, name='detailed_month'),
    path('detailed_month/<month>_<int:year>/<int:pk>/update', login_required(views.ExpenseUpdate.as_view()), name='expense_update'),
    path('detailed_month/<month>_<int:year>/<int:pk>/delete', login_required(views.ExpenseDelete.as_view()), name='expense_delete'),
]
