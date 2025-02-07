from django.urls import path, include
from .views import counselling

urlpatterns = [
    path("counselling/", counselling),
]