from django.db import models
import secrets
import string


class RedeemCodeStatus(models.TextChoices):
    """리딤코드 상태"""
    UNUSED = 'unused', '미사용'
    USED = 'used', '사용됨'
    DELETED = 'deleted', '삭제됨'


class RedeemCode(models.Model):
    """
    이메일 기반 리딤코드 발급 모델
    """
    email = models.EmailField(help_text="사용자 이메일")
    code = models.CharField(max_length=8, unique=True, help_text="8자리 영문 대문자+숫자 리딤코드")
    status = models.CharField(
        max_length=10,
        choices=RedeemCodeStatus.choices,
        default=RedeemCodeStatus.UNUSED,
        help_text="상태 (unused: 미사용, used: 사용됨, deleted: 삭제됨)"
    )
    uuid = models.CharField(max_length=100, null=True, blank=True, help_text="사용자 기기 UUID")
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일")

    def __str__(self):
        return f"{self.email} - {self.code}"

    @classmethod
    def generate_unique_code(cls):
        """
        8자리 영문 대문자 + 숫자 조합의 유니크한 코드를 생성합니다.
        DB에 이미 존재하는 코드라면 재시도합니다.
        """
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(chars) for _ in range(8))
            if not cls.objects.filter(code=code).exists():
                return code
