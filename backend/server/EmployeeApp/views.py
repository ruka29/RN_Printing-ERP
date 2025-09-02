from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmployeeSerializer
from .models import Employee
from django.contrib.auth.hashers import make_password, check_password

class EmployeeCreateView(APIView):
    def post(self, request):
        data = request.data.copy()
        
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            employee = Employee(**serializer.validated_data)
            employee.save()
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)
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

        if check_password(password, employee.password):
            return Response({'message': 'Login successful', 'employee_id': employee.employee_id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        

class EmployeeDetailView(APIView):
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        data = EmployeeSerializer(employee).data
        data.pop('password', None)

        return Response(data, status=status.HTTP_200_OK)
