==============================================================
Gemini AI Chat for Odoo - Odoo 18 User and Technical Guide
==============================================================

.. contents:: Table of Contents
   :depth: 3
   :local:

----

1. Overview
===========

The **Gemini AI Chat for Odoo** module adds a native chat interface for
Google Gemini inside Odoo.

It helps users:

- Create private Gemini chat sessions.
- Ask questions from the Odoo backend.
- Keep user and assistant message history.
- Configure Gemini API settings directly inside this module.
- Set a system prompt per session.
- Override the Gemini model when needed.
- Adjust temperature and max tokens.

The module is designed for Odoo 18 users who want a simple Gemini
assistant before building deeper business-specific AI automations.

----

2. Dependencies
===============

The module depends on:

- ``base``
- ``web``

No separate Gemini module is required.

----

3. Installation
===============

1. Copy ``sm_gemini_chat`` into an Odoo addons path.
2. Restart Odoo.
3. Update Apps List.
4. Install **Gemini AI Chat for Odoo**.
5. Configure Gemini API key in Odoo Settings.

Command-line example:

.. code-block:: bash

   python3 ~/odoo/odoo-18/odoo-server \
      -c ~/odoo/conf/odoo.conf \
      -d your_database \
      -i sm_gemini_chat \
      --stop-after-init \
      --no-http

----

4. Usage
========

Open Chat
---------

1. Open **Gemini AI -> Chat**.
2. Create a new chat session.
3. Type a message.
4. Click **Send**.

Gemini replies in the message list.

System Prompt
-------------

Use the **Instructions** tab to guide Gemini behavior.

Example:

.. code-block:: text

   You are a concise Odoo assistant. Answer in Indonesian.

Model Override
--------------

Leave **Model Override** empty to use Gemini Chat settings.

Set a value only when you want one chat session to use another Gemini
model.

Example:

.. code-block:: text

   gemini-2.5-flash-lite

Temperature
-----------

Lower values make responses more focused.
Higher values make responses more creative.

Recommended default:

.. code-block:: text

   0.7

Max Tokens
----------

Controls maximum Gemini answer length.

Recommended default:

.. code-block:: text

   500

----

5. Security
===========

Users can access their own chat sessions and messages.

Record rules:

- Chat session domain: ``user_id = current user``.
- Chat message domain: ``session_id.user_id = current user``.

The Gemini API key is stored in Odoo system parameters under this module's settings.

----

6. Technical Reference
======================

Models
------

.. code-block:: text

   gemini.chat.session
   gemini.chat.message

Gemini Service
-----------------

The module calls:

.. code-block:: python

   env['sm.gemini.chat.service'].call_ai_chat(messages)

Main Session Method
-------------------

.. code-block:: python

   action_send_message()

This method:

- Creates a user message.
- Builds chat history.
- Calls the built-in Gemini service.
- Creates a Gemini assistant reply.
- Updates last message timestamp.

----

7. Troubleshooting
==================

Gemini API Key Missing
----------------------

Configure the key in **Settings -> Gemini AI Chat**.

Quota Exceeded
--------------

Check Google AI Studio rate limits.
Try another Gemini model or wait for quota reset.

No Reply
--------

Check:

- Gemini Chat test connection works.
- API key is valid.
- Model is available.
- Max tokens is greater than zero.

----

8. Maintainer
=============

.. code-block:: text

   Steven Marp

License:

.. code-block:: text

   OPL-1
