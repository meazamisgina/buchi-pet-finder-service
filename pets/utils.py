from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

def process_pet_photo(photo_file, pet_id, index):
    img = Image.open(photo_file)
    
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)
    
    filename = f"pets/{pet_id}/photo_{index}.jpg"
    
    path = default_storage.save(filename, ContentFile(buffer.read()))
    
    return path