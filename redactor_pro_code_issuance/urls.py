from django.urls import path
from .views import RedeemCodeIssueAPIView, RedeemCodeDashboardView, RedeemCodeValidationAPIView, RedeemCodeValidationTestView

urlpatterns = [
    # API Endpoint
    path('redeem/issue/', RedeemCodeIssueAPIView.as_view(), name='redeem-issue-api'),
    path('redeem/validate/', RedeemCodeValidationAPIView.as_view(), name='redeem-validate-api'),
    
    # Web Dashboard
    path('redeem/dashboard/', RedeemCodeDashboardView.as_view(), name='redeem-dashboard'),
    path('redeem/validation-test/', RedeemCodeValidationTestView.as_view(), name='redeem-validation-test'),
]
