from rest_framework import serializers
from .models import Customer
import re

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_phone(self, value):
        """Validate Ethiopian phone number"""
        phone = re.sub(r'[\s\-]', '', value)
        
        pattern = r'^(09\d{8}|\+251\d{9})$'
        if not re.match(pattern, phone):
            raise serializers.ValidationError(
                "Phone number must be Ethiopian format: 09XXXXXXXX or +251XXXXXXXXX"
            )
        return phone