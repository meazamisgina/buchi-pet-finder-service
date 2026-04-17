from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Customer

class CustomerAPITests(APITestCase):
    def test_create_new_customer(self):
        url = reverse('customer-create')
        data = {
            "name": "Selamawit Tadesse",
            "phone": "0911223344"  
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'created')
        self.assertIn('customer_id', response.data)
        
        customer = Customer.objects.get(phone="0911223344")
        self.assertEqual(customer.name, "Selamawit Tadesse")

    def test_deduplicate_existing_phone(self):
        url = reverse('customer-create')
        
        data1 = {"name": "Dawit Mengistu", "phone": "0922334455"}
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        customer_id_1 = response1.data['customer_id']
        
        data2 = {"name": "Different Name", "phone": "0922334455"}
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['status'], 'already_exists')
        self.assertEqual(response2.data['customer_id'], customer_id_1)
        
        self.assertEqual(Customer.objects.filter(phone="0922334455").count(), 1)

    def test_validate_ethiopian_phone(self):
        url = reverse('customer-create')
        
        valid_phones = ["0911223344", "+251911223344", "0988776655"]
        for phone in valid_phones:
            with self.subTest(phone=phone):
                data = {"name": "Test User", "phone": phone}
                response = self.client.post(url, data, format='json')
                self.assertIn(response.status_code, [200, 201])
        
        invalid_phones = ["123456", "+1234567890", "0711223344"]
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                data = {"name": "Test User", "phone": phone}
                response = self.client.post(url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)