from django.db import models
import uuid

class Adoption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='adoptions')
    pet_id = models.CharField(max_length=100)
    pet_source = models.CharField(max_length=20, choices=[('local', 'Local'), ('thedogapi', 'TheDogAPI')])
    
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['requested_at']
        indexes = [
            models.Index(fields=['requested_at']),
        ]

    def __str__(self):
        return f"Adoption {self.id.hex[:8]} - {self.customer.name}"