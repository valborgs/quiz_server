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
