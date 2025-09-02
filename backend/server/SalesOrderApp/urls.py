from django.urls import path
from .views import *

urlpatterns = [
    path('save/', SalesOrderCreateView.as_view(), name='save_sales_order'),
    path("all/", SalesOrderListView.as_view(), name="sales_order_list"),
    path("<int:sales_order_id>/", SalesOrderDetailView.as_view(), name="sales_order_detail"),
    path('status/<str:status_value>/', SalesOrderByStatusView.as_view(), name='salesorder_by_status'),
]