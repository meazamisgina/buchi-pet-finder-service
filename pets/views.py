from rest_framework import generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import Pet
from .serializers import PetSerializer
from .services import DogAPIService

class PetListCreateView(generics.ListCreateAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def list(self, request, *args, **kwargs):
        local_queryset = self.get_queryset()
        
        pet_type = request.query_params.get('type')
        gender = request.query_params.getlist('gender') 
        size = request.query_params.getlist('size')
        age = request.query_params.getlist('age')
        good_with_children = request.query_params.get('good_with_children')
        limit = int(request.query_params.get('limit', 10))
        
        if pet_type:
            types = [t.strip() for t in pet_type.split(',')]
            local_queryset = local_queryset.filter(type__in=types)
        
        if gender:
            local_queryset = local_queryset.filter(gender__in=gender)
        if size:
            local_queryset = local_queryset.filter(size__in=size)
        if age:
            local_queryset = local_queryset.filter(age__in=age)
        if good_with_children is not None:
            bool_val = good_with_children.lower() in ['true', '1', 'yes']
            local_queryset = local_queryset.filter(good_with_children=bool_val)
        
        local_queryset = local_queryset[:limit]
        local_serializer = self.get_serializer(local_queryset, many=True)
        local_results = local_serializer.data
        
        external_results = []
        if not pet_type or any(t.lower() == 'dog' for t in (pet_type.split(',') if pet_type else [])):
            try:
                external_results = DogAPIService.get_external_dogs(limit=limit)
            except Exception as e:
                print(f"[WARN] DogAPI fetch failed: {e}")
        
        combined = local_results + external_results
        
        combined = combined[:limit]
        
        return Response({
            "status": "success",
            "pets": combined
        })

    def perform_create(self, serializer):
        serializer.save(source='local')