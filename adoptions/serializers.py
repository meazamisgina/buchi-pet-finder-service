from rest_framework import serializers
from .models import Adoption
from customers.models import Customer
from .utils import AdoptionRateLimiter


class AdoptionSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(write_only=True, required=True)
    customer_phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Adoption
        fields = ['id', 'pet_id', 'pet_source', 'customer_name', 'customer_phone', 'requested_at']
        read_only_fields = ['id', 'requested_at', 'pet_source']

    def validate(self, data):
        customer, created = Customer.objects.get_or_create(
            phone=data['customer_phone'],
            defaults={'name': data['customer_name']}
        )
        
        can_proceed, remaining = AdoptionRateLimiter.can_adopt(customer.id)
        if not can_proceed:
            raise serializers.ValidationError(
                "You have reached the daily limit of 5 adoptions. Please try again tomorrow."
            )
        
        data['customer'] = customer
        return data

    def create(self, validated_data):
        customer = validated_data.pop('customer')
        validated_data.pop('customer_name', None)
        validated_data.pop('customer_phone', None)
        
        adoption = Adoption.objects.create(customer=customer, **validated_data)
        AdoptionRateLimiter.increment_count(customer.id)
        return adoption


class AdoptionRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    
    pet_type = serializers.SerializerMethodField()
    pet_gender = serializers.SerializerMethodField()
    pet_size = serializers.SerializerMethodField()
    pet_age = serializers.SerializerMethodField()
    pet_good_with_children = serializers.SerializerMethodField()
    
    class Meta:
        model = Adoption
        fields = [
            'customer_id', 'customer_name', 'customer_phone',
            'pet_id',
            'pet_type', 'pet_gender', 'pet_size', 'pet_age', 'pet_good_with_children',
            'requested_at'
        ]
        read_only_fields = fields

    def _get_local_pet_field(self, adoption, field_name):
        """Helper to safely fetch pet details from local DB"""
        if adoption.pet_source != 'local':
            return None
        try:
            from pets.models import Pet
            pet = Pet.objects.get(id=adoption.pet_id)
            return getattr(pet, field_name, None)
        except:
            return None

    def get_pet_type(self, obj):
        return self._get_local_pet_field(obj, 'type') or ('Dog' if obj.pet_source == 'thedogapi' else None)

    def get_pet_gender(self, obj):
        return self._get_local_pet_field(obj, 'gender') or 'unknown'

    def get_pet_size(self, obj):
        return self._get_local_pet_field(obj, 'size') or 'medium'

    def get_pet_age(self, obj):
        return self._get_local_pet_field(obj, 'age') or 'unknown'

    def get_pet_good_with_children(self, obj):
        val = self._get_local_pet_field(obj, 'good_with_children')
        return val if val is not None else False