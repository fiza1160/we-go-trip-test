from django.urls import path, include
from reviews import views

urlpatterns = [
    path('', views.ReviewList.as_view(), name='review-list'),
]