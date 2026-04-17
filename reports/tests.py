from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from customers.models import Customer
from pets.models import Pet
from adoptions.models import Adoption
from datetime import timedelta

class ReportTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Hana Abebe",
            phone="0933445566"
        )
        self.local_pet = Pet.objects.create(
            type="Cat",
            gender="female",
            size="small",
            age="young",
            good_with_children=True,
            source="local"
        )
        
        self.adoption1 = Adoption.objects.create(
            customer=self.customer,
            pet_id=str(self.local_pet.id),
            pet_source="local",
            requested_at=timezone.now() - timedelta(days=5)
        )
        self.adoption2 = Adoption.objects.create(
            customer=self.customer,
            pet_id="external-dog-id",
            pet_source="thedogapi",
            requested_at=timezone.now() - timedelta(days=3)
        )

    def test_report_generation_format(self):
        url = reverse('report-generate')
        data = {
            "from_date": (timezone.now() - timedelta(days=7)).date().isoformat(),
            "to_date": (timezone.now() + timedelta(days=1)).date().isoformat()
        }
        
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        
        report_data = response.data['data']
        self.assertIn('adopted_pet_types', report_data)
        self.assertIn('weekly_adoption_requests', report_data)
        
        self.assertIn('Cat', report_data['adopted_pet_types'])
        self.assertIn('Dog (External)', report_data['adopted_pet_types'])

    def test_report_date_filtering(self):
        """Report only includes adoptions in date range"""
        url = reverse('report-generate')
        
        data = {
            "from_date": "2020-01-01",
            "to_date": "2020-01-31"
        }
        response = self.client.post(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        report_data = response.data['data']
        self.assertEqual(report_data['adopted_pet_types'], {})
        self.assertEqual(report_data['weekly_adoption_requests'], {})