from rest_framework import serializers
from .models import Pet
from .utils import process_pet_photo

class PetSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Pet
        fields = [
            'id', 'type', 'gender', 'size', 'age', 
            'good_with_children', 'photos', 'source', 
            'uploaded_images', 'created_at'
        ]
        read_only_fields = ['id', 'photos', 'source', 'created_at']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        pet = Pet.objects.create(**validated_data)
        
        photo_paths = []
        for index, image in enumerate(uploaded_images):
            path = process_pet_photo(image, pet.id, index)
            photo_paths.append(path)
        
        pet.photos = photo_paths
        pet.save()
        return pet