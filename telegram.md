# Telegram Bot Integration & Manual Setup Guide

This guide outlines how to configure a custom Telegram Bot, connect it as an interface gateway to the AgriTrace AI Intelligence module, and configure the webhook routes.

---

## 🛠️ Step 1: Create a Bot via @BotFather
1. Open Telegram and search for the official account [@BotFather](https://t.me/botfather).
2. Start a conversation and send the command `/newbot`.
3. Choose a display name for your assistant (e.g. `AgriTrace Helper`).
4. Choose a unique username ending in `bot` (e.g. `agritrace_ai_bot`).
5. BotFather will return your secret **HTTP API Token** (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

Add this key to your `backend/.env` file:
```env
TELEGRAM_BOT_TOKEN=8322419059:AAHGa3GGTJeMczjJGbTJBI696z7vKcYCHI4
TELEGRAM_WEBHOOK_SECRET=agritrace_telegram_secret_123
```

---

## 📡 Step 2: Register the Webhook Endpoint
To register your callback router with the Telegram servers, execute a `POST` request to the Telegram Bot API:
```bash
curl -X POST "https://api.telegram.org/bot123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://yourdomain.com/api/telegram/webhook"}'
```

---

## 🗄️ Step 3: Database Schema Migrations
Ensure the following SQLAlchemy entity tables are migrated:
- **telegram_users**: Holds mapped verified Telegram chat IDs linked to user profile IDs.
- **telegram_conversations**: Logs incoming and outgoing chat turns with unique session IDs.
- **telegram_media**: Saves down crop photos or PDF documents.
- **telegram_notifications**: Logs push warnings.

---

## 🧩 Step 4: Folder Architecture Layout
The integration code is located in the `backend/telegram/` directory:
1. `config.py`: Loads the environment variables.
2. `telegram_service.py`: Contains calls to `/sendMessage`, `/sendPhoto`, and `/sendDocument`.
3. `user_mapper.py`: Performs database mapping searches for chat IDs.
4. `session_manager.py`: Resolves chat history loops.
5. `media_handler.py`: Downloads file attachments (photos, PDFs) from Telegram.
6. `message_parser.py`: Decodes raw Telegram Bot updates.
7. `phone_verification.py`: Handles verification OTP code caching and mapping.
8. `message_queue.py`: Retry queue for failed network updates.
9. `notification_service.py`: Outbound notification pushes.
10. `template_manager.py`: Mapped instructions templates.
11. `response_formatter.py`: Sanitizes text formats.
12. `router.py`: Exposes webhook and API endpoints.

---

## 🤖 Step 5: How Webhook Routing Works
When a message arrives at `/api/telegram/webhook`:
- The parser verifies if the message type is an `image`. If so, it downloads the picture file and executes the Computer Vision diagnostic module (`prediction_service.predict_image_path()`).
- If it is a text query, it passes the context directly to the compiled LangGraph supervisor loop (`agrigraph_compiled.ainvoke()`).
- The response is formatted into standard Telegram markdown layout and dispatched back to the user.

---

## 💻 Step 6: Local Development via Long-Polling (Localhost Compatibility)
For local development, configuring webhooks can be challenging because Telegram cannot send callbacks to `localhost`. 

To solve this, AgriTrace implements an automated **Telegram Long-Polling Engine** (`polling.py`):
1. **Startup**: When you run `python backend/run.py` to start the app, a background task (`start_telegram_polling()`) is automatically registered in FastAPI's `lifespan` handler.
2. **Execution**: The background thread polls the Telegram Bot API `getUpdates` endpoint in a loop, fetching updates directly and feeding them to the same `process_telegram_update` routing block.
3. **No Webhook Required**: This lets you test the bot on `localhost:8000` out of the box simply by configuring the `TELEGRAM_BOT_TOKEN` in your `.env` file.
