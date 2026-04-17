from django.db import models
import uuid

class Pet(models.Model):
    PET_TYPES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Other', 'Other'),
    ]
    
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]
    SIZE_CHOICES = [
        ('small', 'Small'), 
        ('medium', 'Medium'), 
        ('large', 'Large'), 
        ('xlarge', 'X-Large')
    ]
    AGE_CHOICES = [
        ('baby', 'Baby'), 
        ('young', 'Young'), 
        ('adult', 'Adult'), 
        ('senior', 'Senior')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=PET_TYPES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    age = models.CharField(max_length=10, choices=AGE_CHOICES, null=True, blank=True)
    good_with_children = models.BooleanField(default=False)
    
    photos = models.JSONField(default=list)
    
    source = models.CharField(max_length=20, default='local')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', 'good_with_children']),
        ]

    def __str__(self):
        return f"[{self.source.upper()}] {self.type} - {self.id.hex[:8]}"