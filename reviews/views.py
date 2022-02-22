from rest_framework import generics, permissions

from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
