from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adoptions.models import Adoption
from django.utils.dateparse import parse_date
from django.db.models import Count
from django.db.models.functions import TruncWeek
from django.utils import timezone
from datetime import datetime, time

class ReportGenerateView(APIView):
    def post(self, request):
        try:
            from_date_str = request.data.get('from_date')
            to_date_str = request.data.get('to_date')
            
            if not from_date_str or not to_date_str:
                return Response(
                    {"status": "error", "message": "from_date and to_date are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
            
            if not from_date or not to_date:
                return Response(
                    {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if isinstance(from_date, datetime):
                start_dt = from_date
            else:
                start_dt = datetime.combine(from_date, time.min)  
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)
            
            if isinstance(to_date, datetime):
                end_dt = to_date
            else:
                end_dt = datetime.combine(to_date, time.max) 
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)
            
            queryset = Adoption.objects.filter(requested_at__range=[start_dt, end_dt])
            
            adopted_pet_types = {}
            for adoption in queryset.filter(pet_source='local'):
                try:
                    from pets.models import Pet
                    pet = Pet.objects.get(id=adoption.pet_id)
                    pet_type = pet.type
                    adopted_pet_types[pet_type] = adopted_pet_types.get(pet_type, 0) + 1
                except:
                    pass
            
            external_count = queryset.filter(pet_source='thedogapi').count()
            if external_count > 0:
                adopted_pet_types['Dog (External)'] = external_count
            
            weekly_stats = (
                queryset
                .annotate(week=TruncWeek('requested_at'))
                .values('week')
                .annotate(count=Count('id'))
                .order_by('week')
            )

            weekly_adoption_requests = {}
            for stat in weekly_stats:
                week_date = stat['week'].date().isoformat()
                weekly_adoption_requests[week_date] = stat['count']
            
            return Response({
                "status": "success",
                "data": {
                    "adopted_pet_types": adopted_pet_types,
                    "weekly_adoption_requests": weekly_adoption_requests
                }
            })
            
        except Exception as e:
            print(f"[ERROR] Report generation failed: {e}")
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )