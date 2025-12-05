from django.urls import path
from .views import RedeemCodeIssueAPIView, RedeemCodeDashboardView, RedeemCodeValidationAPIView, RedeemCodeValidationTestView, KofiWebhookView

urlpatterns = [
    # API Endpoint
    path('webhook/kofi/', KofiWebhookView.as_view(), name='kofi-webhook'),
    path('redeem/issue/', RedeemCodeIssueAPIView.as_view(), name='redeem-issue-api'),
    path('redeem/validate/', RedeemCodeValidationAPIView.as_view(), name='redeem-validate-api'),
    
    # Web Dashboard
    path('redeem/dashboard/', RedeemCodeDashboardView.as_view(), name='redeem-dashboard'),
    path('redeem/validation-test/', RedeemCodeValidationTestView.as_view(), name='redeem-validation-test'),
]
