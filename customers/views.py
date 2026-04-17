from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer

class CustomerCreateView(generics.GenericAPIView):

    serializer_class = CustomerSerializer
    
    def post(self, request):
        phone = request.data.get('phone')
        name = request.data.get('name')
        
        if not phone:
            return Response({
                'status': 'error',
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        existing_customer = Customer.objects.filter(phone=phone).first()
        
        if existing_customer:
            return Response({
                'status': 'already_exists',
                'customer_id': str(existing_customer.id),
                'message': 'Customer with this phone number already exists'
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                'status': 'created',
                'customer_id': str(customer.id),
                'message': 'New customer created successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)