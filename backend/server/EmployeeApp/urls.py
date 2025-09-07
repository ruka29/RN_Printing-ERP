from django.urls import path
from .views import *

urlpatterns = [
    # ---------------- Existing Endpoints ----------------
    path('add/', EmployeeCreateView.as_view(), name='employee-add'),
    path('login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('get-user/', EmployeeDetailView.as_view(), name='employee-detail'),

    # ---------------- New Endpoints ----------------
    path('all/', EmployeeListView.as_view(), name='employee-list'),
    path('<int:employee_id>/', EmployeeSingleView.as_view(), name='employee-single'),
]