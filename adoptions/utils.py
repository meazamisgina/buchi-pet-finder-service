from django.core.cache import cache
from django.utils import timezone
from .models import Adoption

class AdoptionRateLimiter:
    @staticmethod
    def get_cache_key(customer_id):
        date_str = timezone.now().date().isoformat()
        return f"rate_limit_{customer_id}_{date_str}"

    @staticmethod
    def can_adopt(customer_id, max_limit=5):
        key = AdoptionRateLimiter.get_cache_key(customer_id)
        current_count = cache.get(key, 0)
        
        if current_count >= max_limit:
            return False, 0
        
        return True, max_limit - current_count

    @staticmethod
    def increment_count(customer_id):
        key = AdoptionRateLimiter.get_cache_key(customer_id)
        current_count = cache.get(key, 0)
        cache.set(key, current_count + 1, timeout=86400)