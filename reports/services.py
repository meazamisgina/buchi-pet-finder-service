from django.db.models import Count
from django.db.models.functions import TruncWeek
from adoptions.models import Adoption
from pets.models import Pet

class ReportService:
    @staticmethod
    def get_adoption_stats(from_date, to_date):
        queryset = Adoption.objects.filter(requested_at__range=[from_date, to_date])

        weekly_stats = (
            queryset.annotate(week=TruncWeek('requested_at'))
            .values('week')
            .annotate(count=Count('id'))
            .order_by('week')
        )

        source_stats = queryset.values('pet_source').annotate(count=Count('id'))

        return {
            "total_adoptions": queryset.count(),
            "weekly_breakdown": list(weekly_stats),
            "source_breakdown": list(source_stats),
        }