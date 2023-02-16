from rest_framework import serializers

from kwork.models import Services


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['user', 'title', 'image', 'description', 'price', 'requirements', 'slug']