from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import requests
import os
import json

# Create your views here.
@api_view(['POST'])
def counselling(request):
    counsel_content = request.data.get('counsel_content')
    
    if not counsel_content: 
        return Response({
                'error': 'empty_content',
                'reason': 'counsel_content is required'
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 프롬프트 파일을 읽어오기
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'counsel_prompt.txt') 
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file: 
            prompt_template = file.read()
    except Exception as e:
        return Response(
            {
                'error': 'read_prompt',
                'reason': 'Failed to read prompt'
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 프롬프트에 상담 내용을 삽입 
    prompt = prompt_template.format(counsel_content=counsel_content)

    # Claude API 호출
    api_url = os.environ.get('X_API_URL') 

    headers = { 
        'x-api-key': os.environ.get('X_API_KEY'), 
        'content-type': 'application/json',
        'anthropic-version': '2023-06-01',
        } 
    
    post_data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 1024,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
        }
    
    response = requests.post(
        url = api_url, 
        json = post_data,
        headers = headers
    )

    if response.status_code == 200: 
        return Response(json.loads(response.json()["content"][0]["text"]), status=status.HTTP_200_OK) 
    else: 
        return Response(
            {
                'error': 'api_call_fail',
                'reason': 'Failed to get recommendation from Claude API'
            }, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )