from __future__ import annotations
import json, os
from typing import Any, Dict, List
from google import genai


class LLMProvider:
    def __init__(self, client) -> None:
        self.client = client
    
    def system_prompt(self, tool_specs: List[Dict]) -> str:
        from src.core.agent.prompts import SYSTEM_PROMPT
        return SYSTEM_PROMPT + '\n\nTOOLS:\n' + json.dumps(tool_specs)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        return self.client.chat(messages)
    

class GeminiChatClient:
    '''
    A minimal Gemini client wrapper
    '''
    def __init__(self) -> None:
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise RuntimeError('GEMINI_API_KEY environment variable not set')
        
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Converts role messages to Gemini-compatible format
        contents = []

        for m in messages:
            role = m['role']
            content = m['content']

            if role == 'system':
                contents.append({
                    'role': 'user',
                    'parts': [{ 'text': f'SYSTEM:\n{content}'}]
                })
            elif role == 'tool':
                contents.append({
                    'role': 'user',
                    'parts': [{ 'text': f'TOOL RESULT:\n{content}'}]
                })
            else:
                contents.append({
                    'role': role,
                    'parts': [{ 'text': content}]
                })

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config={
                'temperature': 0.2
            }
        )

        return response.text
        
