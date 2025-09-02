from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=500)
    department_id = serializers.IntegerField()

    def create(self, validated_data):
        emp = Employee(**validated_data)
        emp.save()
        return emp