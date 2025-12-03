from django.urls import path
from .views import RedactPdfView

urlpatterns = [
    path('redact/', RedactPdfView.as_view(), name='redact_pdf'),
]
