from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

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
        sales_orders = SalesOrder.objects(status=status_value)
        if not sales_orders:
            return Response(
                {"message": f"No sales orders found with status '{status_value}'"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SalesOrderSerializer(sales_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
