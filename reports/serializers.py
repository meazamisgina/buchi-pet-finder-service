from rest_framework import serializers

class ReportRequestSerializer(serializers.Serializer):
    from_date = serializers.DateField(required=True, help_text="Start date (YYYY-MM-DD)")
    to_date = serializers.DateField(required=True, help_text="End date (YYYY-MM-DD)")
    
    def validate(self, data):
        if data['from_date'] > data['to_date']:
            raise serializers.ValidationError("from_date cannot be after to_date")
        return data


class ReportResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = serializers.DictField()