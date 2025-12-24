from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import GuestbookEntry
from .serializers import (
    GuestbookListSerializer,
    GuestbookCreateSerializer,
    GuestbookDeleteSerializer,
)


class GuestbookPagination(PageNumberPagination):
    """방명록 페이지네이션 설정"""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class GuestbookListCreateView(APIView):
    """방명록 목록 조회 및 작성 API"""
    authentication_classes = []
    
    def get(self, request):
        """방명록 목록 조회 (페이지네이션 적용)"""
        entries = GuestbookEntry.objects.all()
        paginator = GuestbookPagination()
        paginated = paginator.paginate_queryset(entries, request)
        serializer = GuestbookListSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """방명록 작성"""
        serializer = GuestbookCreateSerializer(data=request.data)
        if serializer.is_valid():
            entry = serializer.save()
            return Response(
                GuestbookListSerializer(entry).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestbookDeleteView(APIView):
    """방명록 삭제 API"""
    authentication_classes = []
    
    def delete(self, request, pk):
        """방명록 삭제 (비밀번호 확인)"""
        try:
            entry = GuestbookEntry.objects.get(pk=pk)
        except GuestbookEntry.DoesNotExist:
            return Response(
                {"error": "not_found", "message": "해당 글을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GuestbookDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not entry.check_password(serializer.validated_data['password']):
            return Response(
                {"error": "password_mismatch", "message": "비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
