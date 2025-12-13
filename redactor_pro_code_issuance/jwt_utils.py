"""
JWT 토큰 생성 및 검증 유틸리티
"""
import jwt
import time
from django.conf import settings


def create_jwt_token(code: str, device_id: str, plan: str = "pro") -> str:
    """
    JWT 토큰을 생성합니다 (exp 없음 → 영구 토큰).
    
    Args:
        code: 리딤코드
        device_id: 기기 UUID
        plan: 요금제 (기본값: "pro")
    
    Returns:
        JWT 토큰 문자열
    """
    payload = {
        "sub": code,
        "device_id": device_id,
        "plan": plan,
        "iat": int(time.time())
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt_token(token: str) -> dict | None:
    """
    JWT 토큰을 검증합니다.
    
    Args:
        token: JWT 토큰 문자열
    
    Returns:
        유효한 경우: 페이로드 딕셔너리 {"sub": ..., "device_id": ..., "plan": ..., "iat": ...}
        무효한 경우: None
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        return None
