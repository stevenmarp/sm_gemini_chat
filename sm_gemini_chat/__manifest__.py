# -*- coding: utf-8 -*-
{
    'name': 'Gemini AI Chat | Google Gemini Chat Assistant',
    'version': '18.0.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Google Gemini chat assistant for Odoo 18 with built-in Gemini API settings, multi-user chat sessions, conversation history, system prompt control, quota tracking, and native Odoo UI.',
    'description': """
Gemini AI Chat for Odoo 18
==========================

Add a practical Google Gemini chat assistant inside Odoo. This module
includes built-in Google Gemini API settings so users can chat with
Gemini from a native Odoo menu without buying or installing another
module.

Main Features
-------------

* Native Odoo Gemini chat sessions
* Google Gemini powered assistant
* Built-in Google Gemini API key settings
* Multi-user private chat history
* User and assistant message timeline
* System prompt control per chat session
* Optional model override per session
* Temperature and max token controls
* Token tracking and monthly usage limit
* Test Gemini connection button in Odoo Settings
* Clean base for future AI chat assistants

Perfect For
-----------

* Odoo users who want a Gemini assistant inside the backend
* Teams testing Google Gemini from Odoo
* Implementers demoing AI features
* Developers building Gemini-powered workflows
* Companies that want chat-based AI before deeper business automation

Search Keywords
---------------

Gemini Chat Odoo, Google Gemini Chat Odoo, Odoo Gemini Assistant,
Odoo AI Chat, Google AI Studio Odoo Chat, Gemini AI Assistant, Odoo
Chatbot, Odoo AI Assistant, Odoo 18 Gemini Chat, Gemini Chatbot Odoo,
AI Chat Odoo, Google Gemini Odoo, Odoo LLM Chat, Odoo Generative AI.
    """,
    'author': 'Steven Marp',
    'website': 'https://apps.odoo.com/apps/browse?order=Newest&repo_maintainer_id=512936',
    'license': 'OPL-1',
    'price': 39.99,
    'currency': 'USD',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/gemini_chat_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/gemini_chat_views.xml',
    ],
    'images': [
        'static/description/banner.gif',
    ],
    'assets': {
        'web.assets_backend': [
            'sm_gemini_chat/static/src/css/gemini_chat.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
