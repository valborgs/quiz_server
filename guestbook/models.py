from django.db import models
import hashlib


class GuestbookEntry(models.Model):
    """방명록 항목 모델"""
    name = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=64)
    content = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '방명록'
        verbose_name_plural = '방명록'

    def __str__(self):
        return f"{self.name}: {self.content[:20]}"

    def set_password(self, raw_password):
        """비밀번호를 SHA256 해시로 저장"""
        self.password_hash = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        """비밀번호 일치 여부 확인"""
        return self.password_hash == hashlib.sha256(raw_password.encode()).hexdigest()
