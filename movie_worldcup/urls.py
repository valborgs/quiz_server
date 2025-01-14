from django.urls import path, include
from .views import monthlyWorldCupInfo, monthlyWorldCupItems

urlpatterns = [
    path("monthlyWorldCupInfo/<int:year>/<int:month>", monthlyWorldCupInfo),
    path("monthlyWorldCupItems/<int:worldCupId>/", monthlyWorldCupItems)
]