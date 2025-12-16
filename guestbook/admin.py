from django.contrib import admin
from .models import GuestbookEntry


@admin.register(GuestbookEntry)
class GuestbookEntryAdmin(admin.ModelAdmin):
    """방명록 관리자 설정"""
    list_display = ['id', 'name', 'content_preview', 'created_at']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'content']
    list_filter = ['created_at']
    readonly_fields = ['password_hash', 'created_at']
    ordering = ['-created_at']

    def content_preview(self, obj):
        """내용 미리보기 (50자)"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '내용'
