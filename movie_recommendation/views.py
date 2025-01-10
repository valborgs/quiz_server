from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import requests
import os
import json

# Create your views here.
@api_view(['POST'])
def recommendMovie(request):
    viewing_history = request.data.get('viewing_history')
    
    if not viewing_history: 
        return Response({'error': 'viewing_history is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 프롬프트 파일을 읽어오기
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'ai_prompt.txt') 
    with open(prompt_path, 'r', encoding='utf-8') as file: 
        prompt_template = file.read()

    # 프롬프트에 시청 기록을 삽입 
    prompt = prompt_template.format(viewing_history=viewing_history)

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
            {'error': 'Failed to get recommendation from Claude API'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )