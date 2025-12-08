from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .models import RedeemCode

class RedeemCodeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_url = reverse('redeem-issue-api')
        self.validation_url = reverse('redeem-validate-api')
        self.dashboard_url = reverse('redeem-dashboard')
        self.validation_test_url = reverse('redeem-validation-test')
        from django.conf import settings
        self.api_key = settings.REDEEM_API_KEY

    def test_validation_test_view(self):
        """검증 테스트 페이지 기능 테스트"""
        from django.contrib.auth.models import User
        admin = User.objects.create_superuser(username='admin_val', password='password', email='admin_val@example.com')
        self.client.login(username='admin_val', password='password')

        # 1. 페이지 접속
        response = self.client.get(self.validation_test_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'redactor_pro_code_issuance/validation_test.html')

        # 2. 유효한 코드 검증
        RedeemCode.objects.create(email='test_val@example.com', code='TESTVAL1')
        data = {'email': 'test_val@example.com', 'code': 'TESTVAL1'}
        response = self.client.post(self.validation_test_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "리딤코드가 성공적으로 검증되었습니다.")
        self.assertTrue(RedeemCode.objects.get(email='test_val@example.com').is_used)

        # 3. 이미 사용된 코드 검증
        response = self.client.post(self.validation_test_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "이미 사용된 리딤코드입니다.")

    def test_validate_code_success(self):
        """리딤코드 검증 성공 테스트"""
        code = RedeemCode.objects.create(email='valid@example.com', code='VALID123')
        
        data = {'email': 'valid@example.com', 'code': 'VALID123'}
        response = self.client.post(
            self.validation_url, 
            data, 
            content_type='application/json',
            HTTP_X_REDEEM_API_KEY=self.api_key
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])
        
        # DB 업데이트 확인
        code.refresh_from_db()
        self.assertTrue(code.is_used)

    def test_validate_code_invalid_header(self):
        """헤더 없이 또는 잘못된 키로 검증 요청 시 실패 테스트"""
        data = {'email': 'valid@example.com', 'code': 'VALID123'}
        
        # 헤더 없음
        response = self.client.post(self.validation_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 잘못된 키
        response = self.client.post(
            self.validation_url, 
            data, 
            content_type='application/json',
            HTTP_X_REDEEM_API_KEY='wrong_key'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_validate_code_already_used(self):
        """이미 사용된 리딤코드 검증 실패 테스트"""
        RedeemCode.objects.create(email='used@example.com', code='USED1234', is_used=True)
        
        data = {'email': 'used@example.com', 'code': 'USED1234'}
        response = self.client.post(
            self.validation_url, 
            data, 
            content_type='application/json',
            HTTP_X_REDEEM_API_KEY=self.api_key
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['is_valid'])

    def test_validate_code_not_found(self):
        """존재하지 않는 리딤코드 검증 실패 테스트"""
        data = {'email': 'unknown@example.com', 'code': 'UNKNOWN1'}
        response = self.client.post(
            self.validation_url, 
            data, 
            content_type='application/json',
            HTTP_X_REDEEM_API_KEY=self.api_key
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['is_valid'])

    def test_validate_code_mismatch(self):
        """이메일과 코드가 일치하지 않는 경우 테스트"""
        RedeemCode.objects.create(email='mismatch@example.com', code='MATCH123')
        
        data = {'email': 'mismatch@example.com', 'code': 'WRONG123'}
        response = self.client.post(
            self.validation_url, 
            data, 
            content_type='application/json',
            HTTP_X_REDEEM_API_KEY=self.api_key
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['is_valid'])

    def test_issue_new_code(self):
        """새 이메일로 리딤코드 발급 테스트"""
        data = {'email': 'new@example.com'}
        response = self.client.post(self.api_url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_new'])
        self.assertIn('code', response.data)
        self.assertEqual(response.data['email'], 'new@example.com')
        
        # DB 저장 확인
        self.assertTrue(RedeemCode.objects.filter(email='new@example.com').exists())

    def test_issue_existing_email(self):
        """이미 존재하는 이메일로 요청 시 새 리딤코드 발급 테스트"""
        # 첫 번째 발급
        self.client.post(self.api_url, {'email': 'exist@example.com'}, content_type='application/json')
        
        # 두 번째 발급
        response = self.client.post(self.api_url, {'email': 'exist@example.com'}, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_new'])
        self.assertEqual(response.data['message'], "새 리딤코드를 발급했습니다.")
        
        # DB에 2개의 코드가 존재하는지 확인
        count = RedeemCode.objects.filter(email='exist@example.com').count()
        self.assertEqual(count, 2)

    def test_invalid_email(self):
        """잘못된 이메일 형식 테스트"""
        data = {'email': 'invalid-email'}
        response = self.client.post(self.api_url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_view_anonymous(self):
        """비로그인 사용자 대시보드 접근 시 로그인 페이지 리다이렉트 테스트"""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/admin/login/?next={self.dashboard_url}')

    def test_dashboard_view_forbidden(self):
        """일반 사용자(비관리자) 대시보드 접근 시 권한 없음 테스트"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='normal', password='password')
        self.client.login(username='normal', password='password')
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 403)

    def test_dashboard_view_staff(self):
        """관리자 계정 대시보드 접근 성공 테스트"""
        from django.contrib.auth.models import User
        admin = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.client.login(username='admin', password='password')
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'redactor_pro_code_issuance/dashboard.html')

    def test_dashboard_issue_code(self):
        """대시보드에서 코드 발급 테스트 (관리자)"""
        from django.contrib.auth.models import User
        admin = User.objects.create_superuser(username='admin2', password='password', email='admin2@example.com')
        self.client.login(username='admin2', password='password')

        data = {'email': 'dashboard@example.com'}
        response = self.client.post(self.dashboard_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'redactor_pro_code_issuance/dashboard.html')
        self.assertContains(response, 'dashboard@example.com')
        self.assertTrue(RedeemCode.objects.filter(email='dashboard@example.com').exists())

    def test_dashboard_context_has_codes(self):
        """대시보드 GET 요청 시 컨텍스트에 리딤코드 목록이 포함되는지 테스트"""
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin_ctx').exists():
            admin = User.objects.create_superuser(username='admin_ctx', password='password', email='admin_ctx@example.com')
        self.client.login(username='admin_ctx', password='password')

        # 리딤코드 생성
        RedeemCode.objects.create(email='ctx1@example.com', code='CTXCODE1')
        RedeemCode.objects.create(email='ctx2@example.com', code='CTXCODE2')

        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('redeem_codes', response.context)
        self.assertEqual(len(response.context['redeem_codes']), 2)

    def test_dashboard_post_updates_context(self):
        """대시보드 POST 요청(발급) 후 컨텍스트에 업데이트된 리딤코드 목록이 포함되는지 테스트"""
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin_mod').exists():
            admin = User.objects.create_superuser(username='admin_mod', password='password', email='admin_mod@example.com')
        self.client.login(username='admin_mod', password='password')

        # 기존 코드 없음
        RedeemCode.objects.all().delete()

        # 코드 발급 요청
        data = {'email': 'post@example.com'}
        response = self.client.post(self.dashboard_url, data)
        self.assertEqual(response.status_code, 200)
        
        # 컨텍스트 확인
        self.assertIn('redeem_codes', response.context)
        self.assertEqual(len(response.context['redeem_codes']), 1)
        self.assertEqual(response.context['redeem_codes'][0].email, 'post@example.com')
