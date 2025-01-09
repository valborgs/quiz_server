from django.urls import path, include
from .views import recommendMovie

urlpatterns = [
    path("recommendation/", recommendMovie),
]