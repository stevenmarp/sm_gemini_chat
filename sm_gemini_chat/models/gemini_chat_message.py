# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GeminiChatMessage(models.Model):
    _name = 'gemini.chat.message'
    _description = 'Gemini Chat Message'
    _order = 'sequence, id'
    _rec_name = 'short_content'

    session_id = fields.Many2one(
        'gemini.chat.session',
        string='Chat Session',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    role = fields.Selection([
        ('user', 'User'),
        ('assistant', 'Gemini'),
        ('system', 'System'),
    ], string='Role', required=True, default='user')
    content = fields.Text(required=True)
    short_content = fields.Char(compute='_compute_short_content', store=True)

    @api.depends('content', 'role')
    def _compute_short_content(self):
        for message in self:
            content = (message.content or '').replace('\n', ' ').strip()
            message.short_content = content[:80] or message.role
