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
    uuid = serializers.CharField(required=True)

    def validate_uuid(self, value):
        return value.replace('-', '')

class RedeemCodeCheckDeviceSerializer(serializers.Serializer):
    """
    리딤코드 기기 정합성 체크 요청 시 코드와 UUID를 검증하는 Serializer
    """
    code = serializers.CharField(required=True, min_length=8, max_length=8)
    uuid = serializers.CharField(required=True)

    def validate_uuid(self, value):
        return value.replace('-', '')
