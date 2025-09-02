from rest_framework import serializers
from .models import SalesOrder, SalesOrderItem

class SalesOrderItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(read_only=True)   # expose generated item_id
    item_description = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.FloatField()

class SalesOrderSerializer(serializers.Serializer):
    sales_order_id = serializers.IntegerField(read_only=True)  # expose generated sales_order_id
    po_no = serializers.CharField()
    po_value = serializers.FloatField()
    currency = serializers.CharField()
    customer = serializers.CharField()
    invoice_address = serializers.CharField()
    delivery_address = serializers.CharField()
    status = serializers.CharField(required=False, default="Pending")
    created_date_time = serializers.DateTimeField(read_only=True)
    created_user = serializers.CharField()
    approved_by = serializers.CharField(allow_null=True, required=False)
    estimated_delivery_time = serializers.DateTimeField(allow_null=True, required=False)
    items = SalesOrderItemSerializer(many=True)

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        sales_order = SalesOrder(**validated_data)
        for item in items_data:
            sales_order.items.append(SalesOrderItem(**item))
        sales_order.save()
        return sales_order