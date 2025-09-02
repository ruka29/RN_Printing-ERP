from django.urls import path
from .views import *

urlpatterns = [
    path('add/', EmployeeCreateView.as_view(), name='employee-add'),
    path('login/', EmployeeLoginView.as_view(), name='employee-login'),
    path('<int:employee_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
]