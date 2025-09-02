import mongoengine as me
from datetime import datetime

class SalesOrderItem(me.EmbeddedDocument):
    item_id = me.SequenceField(primary_key=True)
    item_description = me.StringField(required=True)
    quantity = me.IntField(required=True)
    unit_price = me.FloatField(required=True)

class SalesOrder(me.Document):
    sales_order_id = me.SequenceField(primary_key=True)
    po_no = me.StringField(required=True)
    po_value = me.FloatField(required=True)
    currency = me.StringField(required=True)
    customer = me.StringField(required=True)
    invoice_address = me.StringField(required=True)
    delivery_address = me.StringField(required=True)
    status = me.StringField(choices=["Pending", "Approved", "Rejected", "Processing", "Completed"], default="Pending")
    created_date_time = me.DateTimeField(default=datetime.utcnow)
    created_user = me.StringField(required=True)
    approved_by = me.StringField()
    estimated_delivery_time = me.DateTimeField()
    items = me.EmbeddedDocumentListField(SalesOrderItem)