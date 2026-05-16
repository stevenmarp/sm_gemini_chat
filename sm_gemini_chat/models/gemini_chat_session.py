# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from markupsafe import escape


class GeminiChatSession(models.Model):
    _name = 'gemini.chat.session'
    _description = 'Gemini Chat Session'
    _order = 'write_date desc, id desc'

    name = fields.Char(default='New Gemini Chat', required=True)
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    active = fields.Boolean(default=True)
    message_ids = fields.One2many(
        'gemini.chat.message',
        'session_id',
        string='Messages',
    )
    input_message = fields.Text(string='Message')
    system_prompt = fields.Text(
        default='You are a helpful Gemini assistant inside Odoo. Keep answers clear, practical, and concise.'
    )
    model_override = fields.Char(
        string='Model Override',
        help='Optional Gemini model ID. Leave empty to use Gemini Chat settings.',
    )
    temperature = fields.Float(default=0.7)
    max_tokens = fields.Integer(default=500)
    message_count = fields.Integer(compute='_compute_message_count')
    last_message_at = fields.Datetime(readonly=True)
    chat_html = fields.Html(compute='_compute_chat_html', sanitize=False)

    @api.depends('message_ids')
    def _compute_message_count(self):
        for session in self:
            session.message_count = len(session.message_ids)

    @api.depends('message_ids.content', 'message_ids.role', 'message_ids.create_date')
    def _compute_chat_html(self):
        for session in self:
            messages = session.message_ids.sorted(lambda message: (message.sequence, message.id))
            if not messages:
                session.chat_html = """
                    <div class="sm-gemini-empty">
                        <div class="sm-gemini-empty-title">Start a new Gemini chat</div>
                        <div class="sm-gemini-empty-text">Ask a question below and Gemini will answer here.</div>
                    </div>
                """
                continue

            html_parts = ['<div class="sm-gemini-thread">']
            for message in messages:
                is_assistant = message.role == 'assistant'
                css_role = 'assistant' if is_assistant else 'user'
                author = 'Gemini' if is_assistant else (message.create_uid.name or 'User')
                avatar = 'G' if is_assistant else 'U'
                created = ''
                if message.create_date:
                    created_dt = fields.Datetime.context_timestamp(message, message.create_date)
                    created = created_dt.strftime('%H:%M')
                content = str(escape(message.content or '')).replace('\n', '<br/>')
                html_parts.append(f"""
                    <div class="sm-gemini-message sm-gemini-message-{css_role}">
                        <div class="sm-gemini-avatar">{avatar}</div>
                        <div class="sm-gemini-bubble">
                            <div class="sm-gemini-meta">
                                <span>{escape(author)}</span>
                                <span>{created}</span>
                            </div>
                            <div class="sm-gemini-text">{content}</div>
                        </div>
                    </div>
                """)
            html_parts.append('</div>')
            session.chat_html = ''.join(html_parts)

    def _next_sequence(self):
        self.ensure_one()
        last_message = self.message_ids.sorted(lambda message: (message.sequence, message.id))[-1] if self.message_ids else False
        return (last_message.sequence if last_message else 0) + 10

    def _build_messages(self):
        self.ensure_one()
        messages = []
        if self.system_prompt:
            messages.append({
                'role': 'system',
                'content': self.system_prompt,
            })
        for message in self.message_ids.sorted(lambda item: (item.sequence, item.id)):
            if message.role in ('user', 'assistant'):
                messages.append({
                    'role': message.role,
                    'content': message.content,
                })
        return messages

    def action_send_message(self):
        self.ensure_one()
        content = (self.input_message or '').strip()
        if not content:
            raise UserError("Please enter a message before sending.")

        if self.name == 'New Gemini Chat':
            self.name = content[:60]

        sequence = self._next_sequence()
        self.env['gemini.chat.message'].create({
            'session_id': self.id,
            'sequence': sequence,
            'role': 'user',
            'content': content,
        })
        self.input_message = False

        response = self.env['sm.gemini.chat.service'].call_ai_chat(
            self._build_messages(),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            model=self.model_override or None,
        )
        self.env['gemini.chat.message'].create({
            'session_id': self.id,
            'sequence': sequence + 10,
            'role': 'assistant',
            'content': response,
        })
        self.last_message_at = fields.Datetime.now()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gemini.chat.session',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_clear_messages(self):
        for session in self:
            session.message_ids.unlink()
            session.last_message_at = False
        return True
