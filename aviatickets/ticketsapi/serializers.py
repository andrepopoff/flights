from rest_framework import serializers
from ticketsapi.models import Method


class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = ('id', 'url')
