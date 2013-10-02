from .models import Package
from rest_framework import serializers


class PackageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Package
        fields = ("name", "url", )
