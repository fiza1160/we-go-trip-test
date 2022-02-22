from rest_framework import serializers
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author', 'rating', 'text', 'created', 'is_published']
        read_only_fields = ['is_published']
