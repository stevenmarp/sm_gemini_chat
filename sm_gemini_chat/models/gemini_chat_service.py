# -*- coding: utf-8 -*-

import json
import logging
import re

import requests

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class GeminiChatService(models.AbstractModel):
    _name = 'sm.gemini.chat.service'
    _description = 'Gemini Chat Service'

    def _get_param(self, key, default='', legacy_key=None):
        params = self.env['ir.config_parameter'].sudo()
        value = params.get_param(key, False)
        if not value and legacy_key:
            value = params.get_param(legacy_key, False)
        return value if value not in (False, None) else default

    def _set_param(self, key, value):
        self.env['ir.config_parameter'].sudo().set_param(key, value)

    def _get_gemini_api_key(self):
        return self._get_param(
            'sm_gemini_chat.gemini_api_key',
            '',
            legacy_key='sm_gemini_connector.gemini_api_key',
        )

    def _get_gemini_model(self):
        model = self._get_param(
            'sm_gemini_chat.gemini_model',
            'gemini-2.5-flash-lite',
            legacy_key='sm_gemini_connector.gemini_model',
        )
        if model == 'custom':
            model = self._get_param(
                'sm_gemini_chat.gemini_custom_model',
                '',
                legacy_key='sm_gemini_connector.gemini_custom_model',
            )
        return model or 'gemini-2.5-flash-lite'

    def _get_gemini_api_base_url(self):
        return (self._get_param(
            'sm_gemini_chat.gemini_api_base_url',
            'https://generativelanguage.googleapis.com/v1beta',
            legacy_key='sm_gemini_connector.gemini_api_base_url',
        ) or '').rstrip('/')

    def _get_timeout(self):
        try:
            timeout = int(self._get_param(
                'sm_gemini_chat.request_timeout',
                '30',
                legacy_key='sm_gemini_connector.request_timeout',
            ) or 30)
        except (TypeError, ValueError):
            timeout = 30
        return max(5, min(timeout, 120))

    def _check_gemini_configured(self):
        if not self._get_gemini_api_key():
            raise UserError("Gemini API key is not configured. Set it in Settings > Gemini AI Chat.")
        if not self._get_gemini_api_base_url():
            raise UserError("Gemini API base URL is not configured. Set it in Settings > Gemini AI Chat.")
        return True

    def _check_usage_limit(self):
        try:
            monthly_limit = int(self._get_param(
                'sm_gemini_chat.monthly_token_limit',
                '0',
                legacy_key='sm_gemini_connector.monthly_token_limit',
            ) or 0)
            total_tokens = int(self._get_param(
                'sm_gemini_chat.total_tokens_used',
                '0',
                legacy_key='sm_gemini_connector.total_tokens_used',
            ) or 0)
        except (TypeError, ValueError):
            return
        if monthly_limit and total_tokens >= monthly_limit:
            raise UserError("Gemini Chat monthly token limit reached. Increase the limit or reset usage in Settings.")

    def _track_usage(self, usage):
        if not usage:
            return
        try:
            current_tokens = int(self._get_param(
                'sm_gemini_chat.total_tokens_used',
                '0',
                legacy_key='sm_gemini_connector.total_tokens_used',
            ) or 0)
        except (TypeError, ValueError):
            current_tokens = 0
        new_total = current_tokens + int(usage.get('total_tokens', 0) or 0)
        self._set_param('sm_gemini_chat.total_tokens_used', str(new_total))

    def _sanitize_api_error(self, error):
        error_msg = str(error)
        response = getattr(error, 'response', None)
        if response is not None:
            try:
                error_json = response.json()
                error_msg = error_json.get('error', {}).get('message', error_msg)
            except ValueError:
                error_msg = response.reason or error_msg
        error_msg = re.sub(r'(key=)[^&\s]+', r'\1***', error_msg)
        error_msg = re.sub(r'(x-goog-api-key[=:]\s*)[A-Za-z0-9._\-]+', r'\1***', error_msg)
        return error_msg[:300]

    def _prepare_gemini_payload(self, messages, temperature, max_tokens):
        contents = []
        system_instruction = None

        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')

            if role == 'system':
                system_instruction = content
            elif role == 'assistant':
                contents.append({
                    'role': 'model',
                    'parts': [{'text': content}],
                })
            else:
                contents.append({
                    'role': 'user',
                    'parts': [{'text': content}],
                })

        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
                'topP': 0.95,
                'topK': 40,
            },
        }
        if system_instruction:
            payload['systemInstruction'] = {
                'parts': [{'text': system_instruction}],
            }
        return payload

    @api.model
    def call_gemini_chat(self, messages, temperature=0.7, max_tokens=1000, model=None):
        self._check_gemini_configured()
        self._check_usage_limit()

        api_key = self._get_gemini_api_key()
        model = model or self._get_gemini_model()
        base_url = self._get_gemini_api_base_url()
        endpoint = f'{base_url}/models/{model}:generateContent'

        try:
            response = requests.post(
                endpoint,
                headers={
                    'Content-Type': 'application/json',
                    'x-goog-api-key': api_key,
                },
                json=self._prepare_gemini_payload(messages, temperature, max_tokens),
                timeout=self._get_timeout(),
            )
            response.raise_for_status()
            result = response.json()

            usage_metadata = result.get('usageMetadata', {})
            self._track_usage({
                'prompt_tokens': usage_metadata.get('promptTokenCount', 0),
                'completion_tokens': usage_metadata.get('candidatesTokenCount', 0),
                'total_tokens': usage_metadata.get('totalTokenCount', 0),
            })

            candidates = result.get('candidates', [])
            if not candidates:
                raise UserError("Gemini returned no response candidates.")
            parts = candidates[0].get('content', {}).get('parts', [])
            if not parts:
                raise UserError("Gemini returned an empty response.")
            return parts[0].get('text', '')
        except requests.exceptions.Timeout:
            _logger.error("Gemini API timeout")
            raise UserError("Gemini service timed out. Please try again.")
        except requests.exceptions.RequestException as error:
            error_msg = self._sanitize_api_error(error)
            _logger.error("Gemini API error: %s", error_msg)
            raise UserError(f"Gemini service error: {error_msg}")
        except (KeyError, IndexError, TypeError) as error:
            _logger.error("Gemini response parse error: %s", error)
            raise UserError("Gemini response format is invalid. Please try again.")

    @api.model
    def call_ai_chat(self, messages, temperature=0.7, max_tokens=1000, model=None):
        return self.call_gemini_chat(messages, temperature=temperature, max_tokens=max_tokens, model=model)

    @api.model
    def test_gemini_connection(self):
        return self.call_gemini_chat([
            {
                'role': 'user',
                'content': "Reply with exactly: Gemini connected successfully.",
            }
        ], temperature=0, max_tokens=30)

    @api.model
    def parse_json_response(self, response):
        try:
            cleaned = (response or '').strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            if not cleaned.startswith('{'):
                match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                cleaned = match.group(0) if match else cleaned
            return json.loads(cleaned)
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            _logger.warning("AI JSON parse error: %s", error)
            return {}
