from rest_framework import serializers
from .models import GuestbookEntry
import random


class GuestbookListSerializer(serializers.ModelSerializer):
    """방명록 조회용 시리얼라이저"""
    class Meta:
        model = GuestbookEntry
        fields = ['id', 'name', 'content', 'created_at']


class GuestbookCreateSerializer(serializers.ModelSerializer):
    """방명록 작성용 시리얼라이저"""
    password = serializers.CharField(write_only=True, max_length=20)
    name = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = GuestbookEntry
        fields = ['id', 'name', 'password', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_content(self, value):
        """내용 유효성 검사 - 최대 4줄"""
        lines = value.strip().split('\n')
        if len(lines) > 4:
            raise serializers.ValidationError("최대 4줄까지 입력 가능합니다.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        name = validated_data.get('name', '').strip()
        
        # 이름이 없으면 익명 이름 자동 생성
        if not name:
            adjectives = ['행복한', '즐거운', '멋진', '귀여운', '용감한', '신나는', '따뜻한', '빛나는']
            nouns = ['고양이', '강아지', '토끼', '펭귄', '여우', '판다', '코알라', '햄스터']
            name = f"{random.choice(adjectives)} {random.choice(nouns)}{random.randint(1, 99)}"
            validated_data['name'] = name
        
        entry = GuestbookEntry(**validated_data)
        entry.set_password(password)
        entry.save()
        return entry


class GuestbookDeleteSerializer(serializers.Serializer):
    """방명록 삭제용 시리얼라이저"""
    password = serializers.CharField(max_length=20)
