from django.db import models
import secrets
import string

class RedeemCode(models.Model):
    """
    이메일 기반 리딤코드 발급 모델
    """
    email = models.EmailField(help_text="사용자 이메일")
    code = models.CharField(max_length=8, unique=True, help_text="8자리 영문 대문자+숫자 리딤코드")
    is_used = models.BooleanField(default=False, help_text="사용 여부")
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
