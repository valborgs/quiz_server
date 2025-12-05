from django.test import TestCase, Client
from django.urls import reverse
from .models import RedeemCode
from unittest.mock import patch

class KofiWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('kofi-webhook')
        # 토큰 설정 필요 (기존 tests.py의 다른 테스트들처럼 settings를 이용하거나 override_settings 사용)
        from django.conf import settings
        self.verification_token = 'test_token'
        
    def test_webhook_valid_email(self):
        """이메일이 포함된 유효한 Ko-fi 웹훅 테스트"""
        
        # settings.KOFI_VERIFICATION_TOKEN을 'test_token'으로 가정하고 테스트
        # override_settings를 사용하는 것이 안전하나, 여기서는 간단히 mock 사용
        
        with patch('django.conf.settings.KOFI_VERIFICATION_TOKEN', self.verification_token):
             with patch('redactor_pro_code_issuance.views.send_mail') as mock_send_mail:
                data = {
                    'verification_token': self.verification_token,
                    'message': 'Thanks for the great work! myemail@example.com',
                }
                
                response = self.client.post(self.webhook_url, data, content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(RedeemCode.objects.filter(email='myemail@example.com').exists())
                mock_send_mail.assert_called_once()
                
    def test_webhook_no_email(self):
        """이메일이 없는 Ko-fi 웹훅 테스트"""
        with patch('django.conf.settings.KOFI_VERIFICATION_TOKEN', self.verification_token):
             with patch('redactor_pro_code_issuance.views.send_mail') as mock_send_mail:
                data = {
                    'verification_token': self.verification_token,
                    'message': 'Just a donation without email!',
                }
                
                response = self.client.post(self.webhook_url, data, content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                # 이메일 없으므로 생성되지 않아야 함 (하지만 구현상 이메일 없으면 그냥 넘어감, 200 OK)
                self.assertFalse(RedeemCode.objects.filter(email='unknown').exists())
                mock_send_mail.assert_not_called()

    def test_webhook_invalid_token(self):
        """유효하지 않은 토큰 테스트"""
        with patch('django.conf.settings.KOFI_VERIFICATION_TOKEN', self.verification_token):
            data = {
                'verification_token': 'wrong_token',
                'message': 'hack attempt',
            }
            
            response = self.client.post(self.webhook_url, data, content_type='application/json')
            self.assertEqual(response.status_code, 403)
