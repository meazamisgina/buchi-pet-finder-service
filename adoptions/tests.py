from django.test import TestCase
from django.core.cache import cache
from django.utils import timezone
from customers.models import Customer
from pets.models import Pet
from .models import Adoption
from .utils import AdoptionRateLimiter
from datetime import timedelta

class AdoptionRateLimitTest(TestCase):
    def setUp(self):
        cache.clear()
        self.customer = Customer.objects.create(
            name="Tigist Bekele",  
            phone="0911234567"      
        )

    def test_rate_limit_allows_five(self):
        """Customer can adopt up to 5 times per day"""
        for i in range(5):
            can_adopt, remaining = AdoptionRateLimiter.can_adopt(self.customer.id)
            self.assertTrue(can_adopt)
            AdoptionRateLimiter.increment_count(self.customer.id)
        
        can_adopt, remaining = AdoptionRateLimiter.can_adopt(self.customer.id)
        self.assertFalse(can_adopt)
        self.assertEqual(remaining, 0)

    def test_deduplication_logic(self):
        phone = "0922334455"
        Customer.objects.get_or_create(phone=phone, defaults={'name': 'Abebe Kebede'})
        Customer.objects.get_or_create(phone=phone, defaults={'name': 'Different Name'})
        
        self.assertEqual(Customer.objects.filter(phone=phone).count(), 1)
        customer = Customer.objects.get(phone=phone)
        self.assertEqual(customer.name, 'Abebe Kebede')  

    def test_rate_limit_resets_daily(self):
        for _ in range(5):
            AdoptionRateLimiter.increment_count(self.customer.id)
        
        can_adopt, _ = AdoptionRateLimiter.can_adopt(self.customer.id)
        self.assertFalse(can_adopt)
        
        cache.clear() 
        can_adopt, remaining = AdoptionRateLimiter.can_adopt(self.customer.id)
        self.assertTrue(can_adopt)
        self.assertEqual(remaining, 5)