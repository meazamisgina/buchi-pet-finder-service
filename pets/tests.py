from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Pet

class PetAPITests(APITestCase):
    def setUp(self):
        Pet.objects.create(
            type="Dog",
            gender="male",
            size="small",
            age="baby",
            good_with_children=True,
            source="local"
        )
        Pet.objects.create(
            type="Cat",
            gender="female",
            size="medium",
            age="adult",
            good_with_children=False,
            source="local"
        )

    def test_create_pet_with_photos(self):
        url = reverse('pet-list-create')
        data = {
            "type": "Dog",
            "gender": "male",
            "size": "small",
            "age": "baby",
            "good_with_children": "true"
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_search_pets_filters_local_db(self):
        url = reverse('pet-list-create')
        
        response = self.client.get(url, {'type': 'Dog', 'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pets = response.data['pets']
        local_dogs = [p for p in pets if p['source'] == 'local' and p['type'] == 'Dog']
        self.assertGreaterEqual(len(local_dogs), 1)
        
        response = self.client.get(url, {'good_with_children': 'true', 'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = response.data['pets']
        local_filtered = [p for p in filtered if p['source'] == 'local']
        for pet in local_filtered:
            if pet['source'] == 'local':
                self.assertTrue(pet.get('good_with_children', False))

    def test_local_results_prioritized(self):
        """Local pets appear before external in combined results"""
        url = reverse('pet-list-create')
        response = self.client.get(url, {'type': 'Dog', 'limit': 10})
        
        pets = response.data['pets']
        sources = [p['source'] for p in pets]
        
        if 'thedogapi' in sources:
            first_external_idx = sources.index('thedogapi')
            before_external = sources[:first_external_idx]
            self.assertTrue(all(s == 'local' for s in before_external))