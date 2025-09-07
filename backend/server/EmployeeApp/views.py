from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmployeeSerializer
from .models import Employee
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import jwt
from datetime import datetime, timedelta


# ---------------- Existing Endpoints ---------------- #

class EmployeeCreateView(APIView):
    def post(self, request):
        data = request.data.copy()
        
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            employee = Employee(**serializer.validated_data)
            employee.save()
            emp_data = EmployeeSerializer(employee).data
            emp_data.pop('password', None)  # Remove password from response
            return Response(emp_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EmployeeLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, employee.password):
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        # JWT payload
        payload = {
            "employee_id": str(employee.employee_id),
            "email": employee.email,
            "exp": datetime.utcnow() + timedelta(hours=1)  # 1-hour expiration
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({
            "message": "Login successful",
            "employee_id": employee.employee_id,
            "jwt_token": token
        }, status=status.HTTP_200_OK)
        

class EmployeeDetailView(APIView):
    """
    Get logged-in employee details based on JWT token payload.
    """

    def get(self, request):
        # Get employee_id from JWT payload set in middleware
        employee_id = getattr(request, "user_id", None)

        if not employee_id:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        data = EmployeeSerializer(employee).data
        data.pop('password', None)  # Hide password
        return Response({"user": data}, status=status.HTTP_200_OK)


# ---------------- New Endpoints ---------------- #

class EmployeeListView(APIView):
    """
    Get all employees without passwords.
    """

    def get(self, request):
        employees = Employee.objects.all()
        data = EmployeeSerializer(employees, many=True).data

        for emp in data:
            emp.pop('password', None)

        return Response({"users": data}, status=status.HTTP_200_OK)


class EmployeeByIdView(APIView):
    """
    Get a single employee by employee_id (no password).
    """

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        data = EmployeeSerializer(employee).data
        data.pop('password', None)

        return Response({"user": data}, status=status.HTTP_200_OK)