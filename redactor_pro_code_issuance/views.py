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
        # 헤더 검증
        from django.conf import settings
        api_key = request.headers.get('X-Redeem-Api-Key')
        if not api_key or api_key != settings.REDEEM_API_KEY:
             return Response({
                "message": "권한이 없습니다."
            }, status=status.HTTP_403_FORBIDDEN)

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
            uuid = serializer.validated_data['uuid']
            
            try:
                redeem_code = RedeemCode.objects.get(email=email, code=code)

                # 사용되지 않은 코드라면: 현재 기기에 바인딩하고 사용 처리
                if not redeem_code.is_used:
                    redeem_code.uuid = uuid
                    redeem_code.is_used = True
                    redeem_code.save()
                elif redeem_code.uuid != uuid:
                    # 기기 변경 (License Transfer)
                    redeem_code.uuid = uuid
                    redeem_code.save()
                    
                    return Response({
                        "message": "새로운 기기에서 리딤코드를 등록합니다. 기존 기기에 설치된 앱은 pro 기능이 비활성화 됩니다.",
                        "is_valid": True
                    }, status=status.HTTP_200_OK)
                
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['redeem_codes'] = RedeemCode.objects.all().order_by('-created_at')
        return context

    def post(self, request):
        email = request.POST.get('email')
        # 기본 컨텍스트 (리딤코드 목록 포함)
        context = self.get_context_data()
        
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
        # 새 코드가 추가되었으므로 목록을 다시 쿼리 (또는 위에서 create 후 쿼리해도 됨, 여기서는 확실하게 다시 쿼리)
        context['redeem_codes'] = RedeemCode.objects.all().order_by('-created_at')
            
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
import httpx
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
    def send_slack_notification(self, text):
        webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
        if webhook_url:
            try:
                # httpx.post는 동기 호출이므로 응답을 기다림. 비동기 처리가 필요하면 Celery 등을 고려해야 함.
                # 현재는 간단한 구현을 위해 동기 호출 사용.
                httpx.post(webhook_url, json={"text": text}, timeout=5.0)
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")

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
            verification_token = data.get('verification_token') or data.get('kofi_transaction_id')
            
            if data.get('verification_token') != settings.KOFI_VERIFICATION_TOKEN:
                 logger.warning(f"Invalid Ko-fi token attempt: {data.get('verification_token')}")
                 return Response({"error": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

            # 2. 데이터 추출
            message_text = data.get('message', '')
            amount = data.get('amount', 'N/A')
            currency = data.get('currency', '')
            # 이메일 추출
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message_text)
            
            if email_match:
                email = email_match.group(0)
                logger.info(f"Email detected in Ko-fi message: {email}")
                
                try:
                    # 3. 리딤코드 발급
                    redeem_code = RedeemCode.objects.create(
                        email=email,
                        code=RedeemCode.generate_unique_code()
                    )
                    
                    # 4. 이메일 전송
                    subject = "[PDF Redactor Pro] 구매해 주셔서 감사합니다! 리딤코드가 도착했습니다."
                    email_body = f"""
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
                    
                    send_mail(
                        subject,
                        email_body,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    logger.info(f"Redeem code email sent to {email}")

                    # 5. 성공 Slack 알림
                    slack_message = (
                        f"🎉 *ko-fi 도네이션이 들어왔습니다!*\n"
                        f"- 금액: {amount} {currency}\n"
                        f"- 이메일: {email}\n"
                        f"- 메시지: {message_text}\n"
                        f"- 리딤코드: 발급 및 전송 완료 ({redeem_code.code})"
                    )
                    self.send_slack_notification(slack_message)
                    
                except Exception as e:
                    logger.error(f"Error processing valid donation: {str(e)}")
                    # 에러 Slack 알림
                    error_message = (
                        f"⚠️ *ko-fi 도네이션 처리 중 에러 발생*\n"
                        f"- 금액: {amount} {currency}\n"
                        f"- 이메일: {email}\n"
                        f"- 에러 내용: {str(e)}"
                    )
                    self.send_slack_notification(error_message)
                    # 이미 200 OK를 Ko-fi에 보내는 것이 나을 수 있음 (재전송 방지)
                    # 하지만 여기서는 에러 발생 시 처리 실패로 간주하고 500 리턴
                    return Response({"error": "Internal Processing Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                logger.info("No email found in Ko-fi message.")
                # 이메일이 없는 경우도 알림
                slack_message = (
                    f"🔔 *ko-fi 도네이션 (이메일 없음)*\n"
                    f"- 금액: {amount} {currency}\n"
                    f"- 메시지: {message_text}\n"
                    f"- 리딤코드: 발급되지 않음 (이메일 미감지)"
                )
                self.send_slack_notification(slack_message)

            return Response({"status": "received"}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
             return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ko-fi webhook error: {str(e)}")
            self.send_slack_notification(f"🚨 *Ko-fi Webhook Critical Error*\n{str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
