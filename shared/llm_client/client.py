from __future__ import annotations

from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from .types import ChatMessage, LLMResponse
from .config import LLMConfig, require_env


class LLMClient:
    '''
    Provider-agnostic chat interface

    Supports:
        - OpenAI (Chat Completions via OpenAI SDK)
        - Anthropic (Claude via Anthropic SDK)
    '''

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()

        if self.config.provider not in {'gemini', 'openai', 'anthropic'}:
            raise ValueError(f'Unsupported provider: {self.config.provider}')
        
        self._openai = None
        self._anthropic = None
        self._gemini = None

        if self.config.provider == 'openai':
            from openai import OpenAI
            api_key = require_env('OPENAI_API_KEY')
            self._openai = OpenAI(api_key=api_key)

        if self.config.provider == 'anthropic':
            from anthropic import Anthropic
            api_key = require_env('ANTHROPIC_API_KEY')
            self._anthropic = Anthropic(api_key=api_key)

        if self.config.provider == "gemini":
            from google import genai
            api_key = require_env("GEMINI_API_KEY")
            self._gemini = genai.Client(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=1, max=6))
    def generate(self, messages: List[ChatMessage], max_tokens: int = 600) -> LLMResponse:
        if self.config.provider == 'openai':
            return self._generate_openai(messages=messages, max_tokens=max_tokens)
        
        if self.config.provider == 'anthropic':
            return self._generate_anthropic(messages=messages, max_tokens=max_tokens)
    
        return self._generate_gemini(messages=messages, max_tokens=max_tokens)


    def _generate_openai(self, messages: List[ChatMessage], max_tokens: int) -> LLMResponse:
        assert self._openai is not None
        resp = self._openai.chat.completions.create(
            model = self.config.model,
            messages = [{'role': m.role, 'content': m.content} for m in messages],
            temperature=self.config.temperature,
            max_tokens=max_tokens
        )

        text = resp.choices[0].message.content or ''
        usage = getattr(resp, 'usage', None)
        in_tok = getattr(resp, 'prompt_tokens', None) if usage else None
        out_tok = getattr(resp, 'completion_tokens', None) if usage else None

        return LLMResponse(
            text=text,
            provider='openai',
            model=self.config.model,
            input_tokens=in_tok,
            output_tokens=out_tok
        )
    

    def _generate_anthropic(self, messages: List[ChatMessage], max_tokens: int) -> LLMResponse:
        assert self._anthropic is not None
        # Anthropic supports a top-level system string + user/assistant messages
        system_parts = [m.content for m in messages if m.role == 'system']
        system_text = '\n\n'.join(system_parts).strip() if system_parts else None

        convo = [{'role': m.role, 'content': m.content} for m in messages if m.role != 'system']

        resp = self._anthropic.messages.create(
            model=self.config.model,
            max_tokens=max_tokens,
            temperature=self.config.temperature,
            system=system_text,
            messages=convo
        )

        # resp.content is a list of blocks; take text bocks
        text_blocks = [m.text for m in resp.content if getattr(m, 'type', '') == 'text']
        text = '\n'.join(text_blocks).strip()

        usage = getattr(resp, 'usge', None)
        in_tok = getattr(usage, 'input_tokens', None) if usage else None
        out_tok = getattr(usage, 'output_tokens', None) if usage else None

        return LLMResponse(
            text=text,
            provider='anthropic',
            model=self.config.model,
            input_tokens=in_tok,
            output_tokens=out_tok
        )
    

    def _generate_gemini(self, messages: List[ChatMessage], max_tokens: int) -> LLMResponse:
        assert self._gemini is not None

        # Convert our chat messages into a single prompt string.
        # (Simple + reliable for Day 1; we’ll improve this later for richer turns.)
        system_parts = [m.content for m in messages if m.role == "system"]
        system_text = "\n\n".join(system_parts).strip()

        user_parts = [m.content for m in messages if m.role == "user"]
        user_text = "\n\n".join(user_parts).strip()

        prompt = ""
        
        if system_text:
            prompt += f"SYSTEM:\n{system_text}\n\n"
        prompt += f"USER:\n{user_text}"

        # Generate content
        resp = self._gemini.models.generate_content(
            model=self.config.model,
            contents=prompt,
            # The SDK supports generation config; keep it minimal for now.
            # We'll add safety + richer configs later.
            config={
                "temperature": self.config.temperature,
                "max_output_tokens": max_tokens,
            },
        )

        text = getattr(resp, "text", "") or ""

        # Token usage is available in some responses, but not always surfaced consistently.
        # Keep nullable to stay provider-agnostic.
        return LLMResponse(
            text=text,
            provider="gemini",
            model=self.config.model,
            input_tokens=None,
            output_tokens=None,
        )