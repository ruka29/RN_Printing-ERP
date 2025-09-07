from django.urls import path
from .views import *

urlpatterns = [
    # ---------------- Existing Endpoints ----------------
    path('save/', SalesOrderCreateView.as_view(), name='save_sales_order'),
    path("all/", SalesOrderListView.as_view(), name="sales_order_list"),
    path("<int:sales_order_id>/", SalesOrderDetailView.as_view(), name="sales_order_detail"),
    path('status/<str:status_value>/', SalesOrderByStatusView.as_view(), name='salesorder_by_status'),

    # ---------------- New Endpoints ----------------
    path("user/", UserSalesOrderListView.as_view(), name="user_sales_order_list"),
    path("<int:sales_order_id>/update-status/", SalesOrderStatusUpdateView.as_view(), name="sales_order_status_update"),
    path("save-with-image/", SalesOrderWithImageCreateView.as_view(), name="save_sales_order_with_image"),
    path("analytics/", SalesOrderAnalyticsView.as_view(), name="sales_order_analytics"),
]