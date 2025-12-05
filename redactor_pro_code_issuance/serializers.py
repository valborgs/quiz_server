from rest_framework import serializers
from .models import RedeemCode

class RedeemCodeSerializer(serializers.Serializer):
    """
    리딤코드 발급 요청 시 이메일 입력을 검증하는 Serializer
    """
    email = serializers.EmailField(required=True)

class RedeemCodeValidationSerializer(serializers.Serializer):
    """
    리딤코드 검증 요청 시 이메일과 코드를 검증하는 Serializer
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=8, max_length=8)
