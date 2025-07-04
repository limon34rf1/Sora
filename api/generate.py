from http import HTTPStatus
import json
import os
import re
import requests
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SORA_API_KEY = os.environ.get('SORA_API_KEY')
SORA_URL = "https://api.laozhang.ai/v1/chat/completions"

def get_best_prompt(user_input):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Create detailed Sora prompt in English: {user_input}")
    return response.text

def get_image_from_sora(prompt):
    headers = {
        "Authorization": f"Bearer {SORA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sora-image",
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(SORA_URL, headers=headers, json=payload)
    return re.findall(r"\((https?://[^\s)]+)\)", resp.json()["choices"][0]["message"]["content"])

def handler(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            optimized_prompt = get_best_prompt(prompt)
            image_urls = get_image_from_sora(optimized_prompt)
            return {
                'statusCode': HTTPStatus.OK,
                'body': json.dumps({'image_urls': image_urls})
            }
        except Exception as e:
            return {
                'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
                'body': json.dumps({'error': str(e)})
            }
    return {
        'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
        'body': json.dumps({'error': 'Method not allowed'})
    }
