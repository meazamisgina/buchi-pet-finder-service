from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import Adoption
from .serializers import AdoptionSerializer, AdoptionRequestSerializer


class AdoptionCreateView(generics.CreateAPIView):
    queryset = Adoption.objects.all()
    serializer_class = AdoptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adoption = self.perform_create(serializer)
        
        return Response({
            "status": "success",
            "adoption_id": str(adoption.id)
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()


class AdoptionRequestsView(ListAPIView):
    serializer_class = AdoptionRequestSerializer

    def get_queryset(self):
        queryset = Adoption.objects.select_related('customer').all()
        
        from_date_str = self.request.query_params.get('from_date')
        to_date_str = self.request.query_params.get('to_date')
        
        if from_date_str:
            parsed_date = parse_date(from_date_str)
            if parsed_date:
                if isinstance(parsed_date, datetime):
                    start_dt = parsed_date
                else:
                    start_dt = datetime.combine(parsed_date, time.min)
                if timezone.is_naive(start_dt):
                    start_dt = timezone.make_aware(start_dt)
                queryset = queryset.filter(requested_at__gte=start_dt)
        
        if to_date_str:
            parsed_date = parse_date(to_date_str)
            if parsed_date:
                if isinstance(parsed_date, datetime):
                    end_dt = parsed_date
                else:
                    end_dt = datetime.combine(parsed_date, time.max)
                if timezone.is_naive(end_dt):
                    end_dt = timezone.make_aware(end_dt)
                queryset = queryset.filter(requested_at__lte=end_dt)
        
        return queryset.order_by('requested_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "status": "success",
            "data": serializer.data
        })