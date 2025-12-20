import json
import fitz  # PyMuPDF
from io import BytesIO
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

class RedactPdfView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # API Key 헤더 검증
        from django.conf import settings
        api_key = request.headers.get('X-Redact-Api-Key')
        if not api_key or api_key != settings.REDACT_API_KEY:
             return Response({
                "message": "권한이 없습니다.",
                "error_code": 1001
            }, status=status.HTTP_403_FORBIDDEN)

        # JWT 토큰 검증
        from redactor_pro_code_issuance.jwt_utils import verify_jwt_token
        from redactor_pro_code_issuance.models import RedeemCode
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                "message": "인증이 필요합니다. 리딤코드를 등록해주세요.",
                "error_code": 2001
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Bearer 토큰 추출
        if not auth_header.startswith('Bearer '):
            return Response({
                "message": "유효하지 않은 인증 토큰입니다.",
                "error_code": 2002
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header[7:]  # "Bearer " 이후 부분
        payload = verify_jwt_token(token)
        
        if payload is None:
            return Response({
                "message": "유효하지 않은 인증 토큰입니다.",
                "error_code": 2002
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # DB에서 리딤코드의 현재 device_id 확인
        redeem_code_str = payload.get('sub')
        token_device_id = payload.get('device_id')
        
        try:
            redeem_code = RedeemCode.objects.get(code=redeem_code_str)
            if redeem_code.uuid != token_device_id:
                return Response({
                    "message": "다른 기기에서 Pro 기능이 활성화되어 있습니다. 리딤코드를 다시 등록하면 다른 기기의 Pro 기능이 비활성화됩니다.",
                    "error_code": 2003
                }, status=status.HTTP_401_UNAUTHORIZED)
        except RedeemCode.DoesNotExist:
            return Response({
                "message": "유효하지 않은 인증 토큰입니다.",
                "error_code": 2002
            }, status=status.HTTP_401_UNAUTHORIZED)

        file_obj = request.FILES.get('file')
        redactions_json = request.data.get('redactions')

        if not file_obj or not redactions_json:
            return Response(
                {
                    "message": "필수 파라미터(file, redactions)가 누락되었습니다.",
                    "error_code": 3001
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            redactions = json.loads(redactions_json)
        except json.JSONDecodeError:
            return Response(
                {
                    "message": "마스킹 데이터(redactions) 형식이 올바르지 않습니다.",
                    "error_code": 3002
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Open the PDF from memory
            # file_obj.read() reads the entire file into bytes
            doc = fitz.open(stream=file_obj.read(), filetype="pdf")

            for item in redactions:
                page_index = item.get('pageIndex')
                x = item.get('x')
                y = item.get('y')
                width = item.get('width')
                height = item.get('height')
                # color is not strictly needed for redaction (it just sets the color of the box), 
                # but we can use it if we want to customize the appearance before applying.
                # For now, default black is fine or we can ignore it as apply_redactions handles the removal.
                
                if page_index is None or x is None or y is None or width is None or height is None:
                    continue # Skip invalid items

                if 0 <= page_index < len(doc):
                    page = doc[page_index]
                    # Create rectangle: (x0, y0, x1, y1)
                    # Android coordinates are top-left origin, same as PyMuPDF default.
                    rect = fitz.Rect(x, y, x + width, y + height)
                    
                    # Add redaction annotation
                    # fill=(0, 0, 0) makes it black. 
                    page.add_redact_annot(rect, fill=(0, 0, 0))
            
            # Apply redactions to the whole document
            # apply_redactions() processes all pages by default if called on page? 
            # Actually page.apply_redactions() is for a single page. 
            # doc doesn't have apply_redactions. We need to apply per page or iterate.
            # Let's iterate pages that were modified or just iterate all pages if we want to be safe, 
            # but here we added annotations to specific pages.
            # Wait, page.add_redact_annot adds to that specific page. 
            # So we should call page.apply_redactions() on that page.
            
            # Optimization: Track modified pages to call apply_redactions only on them?
            # Or just apply immediately in the loop? 
            # Applying immediately in the loop might be problematic if multiple redactions are on the same page?
            # No, apply_redactions() applies all pending redaction annotations on that page.
            # So it's better to add all annotations first, then apply.
            
            # Let's group by page index
            pages_to_redact = set()
            for item in redactions:
                page_index = item.get('pageIndex')
                if page_index is not None and 0 <= page_index < len(doc):
                    pages_to_redact.add(page_index)

            # Re-iterate to add annotations (or do it in one pass if we are careful)
            # Actually, we can just add annotations in the loop.
            # Then iterate through unique pages and apply.
            
            # Reset doc stream position? No, we opened it in memory.
            
            # Let's re-structure the loop slightly for clarity
            pass

            # Re-implementation of the loop
            # Helper to convert Android int color to PyMuPDF RGB tuple
            def _int_to_rgb(color_int):
                # Ensure 32-bit unsigned
                color = color_int & 0xFFFFFFFF
                # Extract components (AARRGGBB)
                # alpha = (color >> 24) & 0xFF  # Unused for now
                red = (color >> 16) & 0xFF
                green = (color >> 8) & 0xFF
                blue = color & 0xFF
                # Return normalized tuple (0..1)
                return (red / 255.0, green / 255.0, blue / 255.0)

            for item in redactions:
                page_index = item.get('pageIndex')
                x = item.get('x')
                y = item.get('y')
                width = item.get('width')
                height = item.get('height')
                # Default to black (-16777216) if not provided
                color_int = item.get('color', -16777216)

                if page_index is not None and x is not None and y is not None and width is not None and height is not None:
                     if 0 <= page_index < len(doc):
                        page = doc[page_index]
                        rect = fitz.Rect(x, y, x + width, y + height)
                        
                        rgb_color = _int_to_rgb(color_int)
                        
                        # Add redaction annotation with the specific color
                        page.add_redact_annot(rect, fill=rgb_color)

            # Apply redactions on pages that have them
            # We can just iterate all pages or keep track. 
            # Since we don't know which pages have annotations easily without tracking, 
            # let's just track the indices we touched.
            
            # Actually, let's use the set we created mentally
            pages_with_redactions = set()
            for item in redactions:
                 if 'pageIndex' in item:
                     pages_with_redactions.add(item['pageIndex'])
            
            for page_idx in pages_with_redactions:
                if 0 <= page_idx < len(doc):
                    page = doc[page_idx]
                    page.apply_redactions()

            # Save to buffer
            output_buffer = BytesIO()
            doc.save(output_buffer)
            doc.close()
            output_buffer.seek(0)

            return FileResponse(
                output_buffer,
                as_attachment=True,
                filename="redacted_result.pdf",
                content_type="application/pdf"
            )

        except Exception as e:
            return Response(
                {
                    "message": f"서버 내부 오류가 발생했습니다: {str(e)}",
                    "error_code": 5001
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
