import httpx
from django.conf import settings

class DogAPIService:
    @staticmethod
    def get_external_dogs(limit=10):
        url = f"{settings.DOG_API_BASE_URL}/images/search"
        headers = {"x-api-key": getattr(settings, 'DOG_API_KEY', '')}
        params = {
            "limit": limit,
            "has_breeds": 1,
            "order": "RANDOM"
        }
        
        try:
            with httpx.Client(timeout=settings.DOG_API_TIMEOUT) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return DogAPIService._format_response(response.json())
        except Exception as e:
            print(f"DogAPI Error: {e}")
            return []

    @staticmethod
    def _format_response(external_data):
        formatted_pets = []
        for item in external_data:
            breeds = item.get('breeds', [])
            breed = breeds[0] if breeds else {}
            
            formatted_pets.append({
                "id": item.get('id'),
                "type": "Dog",
                "gender": "unknown",
                "size": DogAPIService._map_size(breed.get('weight', {}).get('metric', '')),
                "age": "unknown",
                "good_with_children": "child" in breed.get('temperament', '').lower() if breed.get('temperament') else False,
                "photos": [item.get('url')],
                "source": "thedogapi"
            })
        return formatted_pets

    @staticmethod
    def _map_size(weight_str):
        try:
            weight = int(weight_str.split('-')[0].strip())
            if weight < 10: return 'small'
            if weight < 25: return 'medium'
            return 'large'
        except:
            return 'medium'