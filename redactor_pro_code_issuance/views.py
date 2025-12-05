from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import RedeemCode
from .serializers import RedeemCodeSerializer, RedeemCodeValidationSerializer

class RedeemCodeIssueAPIView(APIView):
    """
    이메일 리딤코드 발급 API
    POST /api/redeem/issue/
    """
    def post(self, request):
        serializer = RedeemCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # 항상 새로운 리딤코드 생성
            redeem_code = RedeemCode.objects.create(
                email=email,
                code=RedeemCode.generate_unique_code()
            )
            
            return Response({
                "email": redeem_code.email,
                "code": redeem_code.code,
                "is_new": True,
                "message": "새 리딤코드를 발급했습니다."
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RedeemCodeValidationAPIView(APIView):
    """
    리딤코드 검증 및 사용 처리 API
    POST /api/redeem/validate/
    """
    def post(self, request):
        # 헤더 검증
        from django.conf import settings
        api_key = request.headers.get('X-Redeem-Api-Key')
        if not api_key or api_key != settings.REDEEM_API_KEY:
             return Response({
                "message": "권한이 없습니다."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = RedeemCodeValidationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                redeem_code = RedeemCode.objects.get(email=email, code=code)
                
                if redeem_code.is_used:
                    return Response({
                        "message": "이미 사용된 리딤코드입니다.",
                        "is_valid": False
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                redeem_code.is_used = True
                redeem_code.save()
                
                return Response({
                    "message": "리딤코드가 성공적으로 검증되었습니다.",
                    "is_valid": True
                }, status=status.HTTP_200_OK)
                
            except RedeemCode.DoesNotExist:
                return Response({
                    "message": "유효하지 않은 이메일 또는 리딤코드입니다.",
                    "is_valid": False
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class RedeemCodeDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    웹 대시보드 뷰
    관리자 권한(is_staff or is_superuser)이 있는 사용자만 접근 가능
    """
    template_name = "redactor_pro_code_issuance/dashboard.html"
    login_url = '/admin/login/'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def post(self, request):
        email = request.POST.get('email')
        context = {}
        
        if not email:
            context['error'] = "이메일을 입력해주세요."
            return render(request, self.template_name, context)
            
        # 간단한 이메일 형식 체크 (필요시 더 정교하게)
        if '@' not in email:
             context['error'] = "유효한 이메일 형식이 아닙니다."
             return render(request, self.template_name, context)

        redeem_code = RedeemCode.objects.create(
            email=email,
            code=RedeemCode.generate_unique_code()
        )
        
        context['redeem_code'] = redeem_code
        context['is_new'] = True
        context['message'] = "새 리딤코드가 발급되었습니다."
            
        return render(request, self.template_name, context)

class RedeemCodeValidationTestView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    리딤코드 검증 테스트 페이지 뷰
    관리자 권한 필요
    """
    template_name = "redactor_pro_code_issuance/validation_test.html"
    login_url = '/admin/login/'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def post(self, request):
        email = request.POST.get('email')
        code = request.POST.get('code')
        context = {}
        
        if not email or not code:
            context['error'] = "이메일과 코드를 모두 입력해주세요."
            return render(request, self.template_name, context)

        try:
            redeem_code = RedeemCode.objects.get(email=email, code=code)
            
            if redeem_code.is_used:
                context['error'] = "이미 사용된 리딤코드입니다."
                context['is_valid'] = False
            else:
                redeem_code.is_used = True
                redeem_code.save()
                context['message'] = "리딤코드가 성공적으로 검증되었습니다."
                context['is_valid'] = True
                context['redeem_code'] = redeem_code
                
        except RedeemCode.DoesNotExist:
            context['error'] = "유효하지 않은 이메일 또는 리딤코드입니다."
            context['is_valid'] = False
            
        return render(request, self.template_name, context)

import json
import re
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class KofiWebhookView(APIView):
    """
    Ko-fi Webhook 처리 뷰
    POST /api/webhook/kofi/
    """
    def post(self, request):
        try:
            # content_type에 따라 데이터 파싱
            if request.content_type == 'application/x-www-form-urlencoded':
                data_str = request.POST.get('data')
                if not data_str:
                     return Response({"error": "No data field provided"}, status=status.HTTP_400_BAD_REQUEST)
                data = json.loads(data_str)
            else:
                 data = request.data

            # 1. Verification Token 검증
            verification_token = data.get('verification_token') or data.get('kofi_transaction_id') # kofi 문서 참조 필요, 보통 verification_token 사용
            
            # Ko-fi 문서에 따르면 data JSON 안에 verification_token이 포함됨
            if data.get('verification_token') != settings.KOFI_VERIFICATION_TOKEN:
                 logger.warning(f"Invalid Ko-fi token attempt: {data.get('verification_token')}")
                 return Response({"error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

            # 2. 메시지에서 이메일 추출
            message_text = data.get('message', '')
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message_text)
            
            if email_match:
                email = email_match.group(0)
                logger.info(f"Email detected in Ko-fi message: {email}")
                
                # 3. 리딤코드 발급
                redeem_code = RedeemCode.objects.create(
                    email=email,
                    code=RedeemCode.generate_unique_code()
                )
                
                # 4. 이메일 전송
                subject = "[PDF Redactor Pro] 구매해 주셔서 감사합니다! 리딤코드가 도착했습니다."
                message = f"""
안녕하세요, 후원자님!

PDF Redactor Pro를 후원해 주셔서 진심으로 감사드립니다.
요청하신 리딤코드를 보내드립니다.

리딤코드: {redeem_code.code}

[앱에서 등록 방법]
1. 앱 설정 메뉴로 이동합니다.
2. '프로 버전 활성화'를 클릭합니다.
3. 위 리딤코드를 입력합니다.

문제가 있거나 궁금한 점이 있으시면 언제든지 문의해 주세요.
감사합니다.
                """
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    logger.info(f"Redeem code email sent to {email}")
                except Exception as e:
                    logger.error(f"Failed to send email to {email}: {str(e)}")
                    # 이메일 전송 실패하더라도 로직은 성공으로 처리하거나, 별도 재시도 로직 필요 (여기선 로그만 남김)

                # TODO: Slack 알림 전송 기능 추가
                
            else:
                logger.info("No email found in Ko-fi message.")

            return Response({"status": "received"}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
             return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ko-fi webhook error: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
