# 방명록 API 명세서 (Django REST Framework)

---

## 1. 방명록 목록 조회

**`GET /guestbook/`**

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | 페이지 번호 (기본값: 1) |
| page_size | integer | No | 페이지당 항목 수 (기본값: 5, 최대: 20) |

### Response (200 OK)
```json
{
    "count": 25,
    "next": "https://your-domain.com/api/v1/guestbook/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "행복한 고양이42",
            "content": "응원합니다!",
            "created_at": "2025-12-16T21:30:00Z"
        }
    ]
}
```

---

## 2. 방명록 작성

**`POST /guestbook/`**

### Request Body
```json
{
    "name": "사용자 이름",
    "password": "삭제용 비밀번호",
    "content": "방명록 내용"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| name | string | No | 최대 20자. 미입력 시 서버에서 익명 이름 생성 |
| password | string | Yes | 최대 20자. 삭제 시 본인 확인용 |
| content | string | Yes | 최대 200자, 4줄 이하 |

### Response (201 Created)
```json
{
    "id": 3,
    "name": "사용자 이름",
    "content": "방명록 내용",
    "created_at": "2025-12-16T22:00:00Z"
}
```

### Error (400 Bad Request)
```json
{
    "content": ["이 필드는 필수입니다."],
    "password": ["이 필드는 필수입니다."]
}
```

---

## 3. 방명록 삭제

**`DELETE /guestbook/{id}/`**

### Request Body
```json
{
    "password": "삭제용 비밀번호"
}
```

### Response (204 No Content)
성공 시 응답 본문 없음

### Error Responses

**400 Bad Request - 비밀번호 불일치**
```json
{
    "error": "password_mismatch",
    "message": "비밀번호가 일치하지 않습니다."
}
```

**404 Not Found - 해당 글 없음**
```json
{
    "error": "not_found",
    "message": "해당 글을 찾을 수 없습니다."
}
```

---

## Django 구현 예시

### models.py
```python
from django.db import models
import hashlib

class GuestbookEntry(models.Model):
    name = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=64)
    content = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def set_password(self, raw_password):
        self.password_hash = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        return self.password_hash == hashlib.sha256(raw_password.encode()).hexdigest()
```

### serializers.py
```python
from rest_framework import serializers
from .models import GuestbookEntry
import random

class GuestbookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestbookEntry
        fields = ['id', 'name', 'content', 'created_at']

class GuestbookCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=20)
    name = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = GuestbookEntry
        fields = ['id', 'name', 'password', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_content(self, value):
        lines = value.strip().split('\n')
        if len(lines) > 4:
            raise serializers.ValidationError("최대 4줄까지 입력 가능합니다.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        name = validated_data.get('name', '').strip()
        
        if not name:
            adjectives = ['행복한', '즐거운', '멋진', '귀여운', '용감한']
            nouns = ['고양이', '강아지', '토끼', '펭귄', '여우']
            name = f"{random.choice(adjectives)} {random.choice(nouns)}{random.randint(1, 99)}"
            validated_data['name'] = name
        
        entry = GuestbookEntry(**validated_data)
        entry.set_password(password)
        entry.save()
        return entry

class GuestbookDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=20)
```

### views.py
```python
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import GuestbookEntry
from .serializers import *

class GuestbookPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20

class GuestbookListCreateView(APIView):
    def get(self, request):
        entries = GuestbookEntry.objects.all()
        paginator = GuestbookPagination()
        paginated = paginator.paginate_queryset(entries, request)
        serializer = GuestbookListSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = GuestbookCreateSerializer(data=request.data)
        if serializer.is_valid():
            entry = serializer.save()
            return Response(GuestbookListSerializer(entry).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GuestbookDeleteView(APIView):
    def delete(self, request, pk):
        try:
            entry = GuestbookEntry.objects.get(pk=pk)
        except GuestbookEntry.DoesNotExist:
            return Response({"error": "not_found", "message": "해당 글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GuestbookDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not entry.check_password(serializer.validated_data['password']):
            return Response({"error": "password_mismatch", "message": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### urls.py
```python
from django.urls import path
from .views import GuestbookListCreateView, GuestbookDeleteView

urlpatterns = [
    path('guestbook/', GuestbookListCreateView.as_view(), name='guestbook-list-create'),
    path('guestbook/<int:pk>/', GuestbookDeleteView.as_view(), name='guestbook-delete'),
]
```
