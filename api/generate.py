import os
import re
import requests
import json
from http.server import BaseHTTPRequestHandler
from google import generativeai as genai

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SORA_API_KEY = os.environ.get('SORA_API_KEY')
SORA_URL = "https://api.laozhang.ai/v1/chat/completions"

def get_best_prompt(user_input):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    response = model.generate_content(
        "Напиши очень подробный промпт для Sora, кроме промпта не должно быть лишних слов. "
        "Задача нарисовать картинку в лучшем виде, не придумывать много лишнего, "
        "главная задача сохранить исходную идею, ниже запрос пользователя, ответ на английском языке:\n"
        f"{user_input}"
    )
    return response.text

def get_image_from_sora(best_prompt):
    headers = {
        "Authorization": f"Bearer {SORA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sora-image",
        "stream": False,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": best_prompt}
        ],
    }
    resp = requests.post(SORA_URL, headers=headers, json=payload)
    return extract_image_urls(resp.json())

def extract_image_urls(data):
    content = data["choices"][0]["message"]["content"]
    return re.findall(r"\((https?://[^\s)]+)\)", content)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            user_input = data.get('prompt', '')
            
            if not user_input:
                raise ValueError("Пустой запрос")
                
            prompt = get_best_prompt(user_input)
            
            image_urls = get_image_from_sora(prompt)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "image_urls": image_urls
            }).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, message=str(e))