from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import SalesOrder
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.utils.timezone import now


# ---------------- Existing Endpoints ---------------- #

class SalesOrderCreateView(APIView):
    def post(self, request):
        serializer = SalesOrderSerializer(data=request.data)
        if serializer.is_valid():
            sales_order = SalesOrder(**serializer.validated_data)
            sales_order.save()
            return Response({"sales_order_id": sales_order.sales_order_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesOrderListView(APIView):
    def get(self, request):
        sales_orders = SalesOrder.objects.all()
        serializer = SalesOrderSerializer(sales_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesOrderDetailView(APIView):
    def get(self, request, sales_order_id):
        try:
            sales_order = SalesOrder.objects.get(sales_order_id=sales_order_id)
            serializer = SalesOrderSerializer(sales_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SalesOrder.DoesNotExist:
            return Response(
                {"error": "Sales order not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SalesOrderByStatusView(APIView):
    def get(self, request, status_value):
        sales_orders = SalesOrder.objects.filter(status=status_value)
        if not sales_orders.exists():
            return Response(
                {"message": f"No sales orders found with status '{status_value}'"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SalesOrderSerializer(sales_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------- New Endpoints ---------------- #

class UserSalesOrderListView(APIView):
    """
    Get all sales orders excluding 'Pending' for the logged-in user.
    """

    def get(self, request):
        employee_id = getattr(request, "user_id", None)
        if not employee_id:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        sales_orders = SalesOrder.objects.filter(created_by=employee_id).exclude(status="Pending")
        serializer = SalesOrderSerializer(sales_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesOrderStatusUpdateView(APIView):
    """
    Update the status of a sales order.
    """

    def patch(self, request, sales_order_id):
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sales_order = SalesOrder.objects.get(sales_order_id=sales_order_id)
            sales_order.status = new_status
            sales_order.save()
            return Response({"message": "Status updated successfully"}, status=status.HTTP_200_OK)
        except SalesOrder.DoesNotExist:
            return Response({"error": "Sales order not found"}, status=status.HTTP_404_NOT_FOUND)


class SalesOrderWithImageCreateView(APIView):
    """
    Save sales order with image upload.
    """

    def post(self, request):
        serializer = SalesOrderSerializer(data=request.data)
        if serializer.is_valid():
            sales_order = serializer.save()
            # If image is included
            image = request.FILES.get("image")
            if image:
                sales_order.image = image
                sales_order.save()
            return Response({"sales_order_id": sales_order.sales_order_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesOrderAnalyticsView(APIView):
    """
    Returns analytics:
    - Total PO count this month
    - Total approved PO count this month
    - Today's created sales orders total PO value
    - Last 7 days total PO value (daily)
    """

    def get(self, request):
        today = now().date()
        start_of_month = today.replace(day=1)
        last_7_days = today - timedelta(days=6)

        # Total PO count this month
        total_po_count = SalesOrder.objects.filter(created_at__date__gte=start_of_month).count()

        # Total approved PO count this month
        approved_po_count = SalesOrder.objects.filter(
            created_at__date__gte=start_of_month,
            status="Approved"
        ).count()

        # Today's total PO value
        today_total_value = SalesOrder.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum("total_price"))["total"] or 0

        # Last 7 days daily totals
        last_7_days_orders = SalesOrder.objects.filter(
            created_at__date__gte=last_7_days
        ).values("created_at__date").annotate(
            daily_total=Sum("total_price")
        ).order_by("created_at__date")

        last_7_days_data = [
            {
                "date": entry["created_at__date"],
                "total_value": entry["daily_total"] or 0
            }
            for entry in last_7_days_orders
        ]

        return Response({
            "total_po_count_this_month": total_po_count,
            "approved_po_count_this_month": approved_po_count,
            "today_total_po_value": today_total_value,
            "last_7_days_total_values": last_7_days_data
        }, status=status.HTTP_200_OK)