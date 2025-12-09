from django.test import TestCase, RequestFactory, override_settings
from unittest.mock import patch, MagicMock
from .views import RedactPdfView
import json
from io import BytesIO

@override_settings(REDACT_API_KEY='test_secret_key')
class RedactPdfViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = RedactPdfView.as_view()

    @patch('pdfredactor.views.fitz')
    def test_post_valid_redaction_with_color(self, mock_fitz):
        # Mock fitz.open
        mock_doc = MagicMock()
        mock_fitz.open.return_value = mock_doc
        # Mock page
        mock_page = MagicMock()
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__len__.return_value = 1
        
        # Prepare file and data
        file_content = b"dummy pdf content"
        file = BytesIO(file_content)
        file.name = "test.pdf"
        
        # Red color: A=255, R=255, G=0, B=0 -> 0xFFFF0000 -> -65536
        red_color_int = -65536
        
        redactions = [
            {
                "pageIndex": 0,
                "x": 10,
                "y": 20,
                "width": 100,
                "height": 50,
                "color": red_color_int
            }
        ]
        
        data = {
            'file': file,
            'redactions': json.dumps(redactions)
        }
        
        # Include API Key in header
        request = self.factory.post(
            '/redact/', 
            data, 
            format='multipart',
            HTTP_X_REDACT_API_KEY='test_secret_key'
        )
        response = self.view(request)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify color conversion
        # -65536 -> 0xFFFF0000 (after & 0xFFFFFFFF) -> R=FF, G=00, B=00 -> (1.0, 0.0, 0.0)
        expected_fill = (1.0, 0.0, 0.0)
        
        # Verify page.add_redact_annot call
        args, kwargs = mock_page.add_redact_annot.call_args
        self.assertEqual(kwargs['fill'], expected_fill)

    def test_post_missing_api_key(self):
        file_content = b"dummy pdf content"
        file = BytesIO(file_content)
        file.name = "test.pdf"
        data = {'file': file, 'redactions': '[]'}
        
        # No API Key
        request = self.factory.post('/redact/', data, format='multipart')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], "권한이 없습니다.")

    def test_post_invalid_api_key(self):
        file_content = b"dummy pdf content"
        file = BytesIO(file_content)
        file.name = "test.pdf"
        data = {'file': file, 'redactions': '[]'}
        
        # Invalid API Key
        request = self.factory.post(
            '/redact/', 
            data, 
            format='multipart', 
            HTTP_X_REDACT_API_KEY='wrong_key'
        )
        response = self.view(request)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], "권한이 없습니다.")
