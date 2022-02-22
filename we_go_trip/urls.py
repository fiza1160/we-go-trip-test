from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('reviews/', include('reviews.urls')),
    path('', RedirectView.as_view(url='/reviews/', permanent=True)),

]