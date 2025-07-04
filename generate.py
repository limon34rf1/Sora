import os
import re
import requests
import google.generativeai as genai
from http import HTTPStatus

GEMINI_API_KEY = 'AIzaSyBjCMFPAv1QX5ewcb0m08Pjh4Mdn6MV9i8'
SORA_API_KEY = 'sk-bCREbtCgwOgFPHxdFd4c7a9910A140438507D1C51401827c'

def handler(request):
    try:
        # Get user input
        data = request.get_json()
        user_input = data.get('prompt', '')
        
        if not user_input:
            return {
                'statusCode': HTTPStatus.BAD_REQUEST,
                'body': {'error': 'Prompt is required'}
            }

        # Generate enhanced prompt with Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = model.generate_content(
            f"Create detailed Sora prompt in English for: {user_input}. "
            "Be specific about visual details but keep it concise."
        ).text

        # Get image from Sora
        headers = {
            "Authorization": f"Bearer {SORA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sora-image",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(
            "https://api.laozhang.ai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        # Extract image URL
        content = response.json()["choices"][0]["message"]["content"]
        image_urls = re.findall(r"\((https?://[^\s)]+)\)", content)

        return {
            'statusCode': HTTPStatus.OK,
            'body': {
                'image_urls': image_urls,
                'prompt': prompt
            }
        }

    except Exception as e:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': {'error': str(e)}
        }
