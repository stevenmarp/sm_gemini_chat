# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sm_gemini_chat_gemini_api_key = fields.Char(
        string='Gemini API Key',
        config_parameter='sm_gemini_chat.gemini_api_key',
        help='Google Gemini API key from Google AI Studio',
    )
    sm_gemini_chat_gemini_model = fields.Selection([
        ('gemini-2.5-flash-lite', 'Gemini 2.5 Flash Lite'),
        ('gemini-2.5-flash', 'Gemini 2.5 Flash'),
        ('gemini-2.5-pro', 'Gemini 2.5 Pro'),
        ('gemini-flash-latest', 'Gemini Flash Latest'),
        ('gemini-2.0-flash', 'Gemini 2 Flash'),
        ('gemini-2.0-flash-lite', 'Gemini 2 Flash Lite'),
        ('custom', 'Custom Model ID'),
    ], string='Gemini Model',
        default='gemini-2.5-flash-lite',
        config_parameter='sm_gemini_chat.gemini_model',
        help='Default Gemini model used by Gemini Chat'
    )
    sm_gemini_chat_gemini_custom_model = fields.Char(
        string='Custom Gemini Model ID',
        config_parameter='sm_gemini_chat.gemini_custom_model',
        help='Use this when Google AI Studio exposes a model not listed here',
    )
    sm_gemini_chat_gemini_api_base_url = fields.Char(
        string='Gemini API Base URL',
        default='https://generativelanguage.googleapis.com/v1beta',
        config_parameter='sm_gemini_chat.gemini_api_base_url',
        help='Default Google Generative Language API base URL',
    )
    sm_gemini_chat_request_timeout = fields.Integer(
        string='Request Timeout',
        default=30,
        config_parameter='sm_gemini_chat.request_timeout',
        help='HTTP request timeout in seconds',
    )
    sm_gemini_chat_tokens_used = fields.Integer(
        string='Total Tokens Used',
        compute='_compute_sm_gemini_chat_tokens_used',
    )
    sm_gemini_chat_monthly_token_limit = fields.Integer(
        string='Monthly Token Limit',
        default=100000,
        config_parameter='sm_gemini_chat.monthly_token_limit',
        help='Maximum tokens per month. Use 0 for unlimited.',
    )

    @api.depends()
    def _compute_sm_gemini_chat_tokens_used(self):
        tokens = int(self.env['ir.config_parameter'].sudo().get_param(
            'sm_gemini_chat.total_tokens_used', '0'
        ) or 0)
        for record in self:
            record.sm_gemini_chat_tokens_used = tokens

    def action_sm_gemini_chat_test_gemini_connection(self):
        try:
            response = self.env['sm.gemini.chat.service'].test_gemini_connection()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Gemini Connected',
                    'message': response[:100],
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as error:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Gemini Connection Failed',
                    'message': str(error)[:200],
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_sm_gemini_chat_reset_token_counter(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'sm_gemini_chat.total_tokens_used', '0'
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Counter Reset',
                'message': 'Gemini Chat token usage counter has been reset to 0',
                'type': 'success',
                'sticky': False,
            }
        }
