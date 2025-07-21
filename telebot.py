import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests

# Voice handling
import speech_recognition as sr
from pydub import AudioSegment

# Set your tokens and paths
TELEGRAM_BOT_TOKEN = "8087239641:AAFq4VXBwKbfY0_5RjmZKXG-VwGNM3Yn4ZA"
GOOGLE_CREDENTIALS = "credentials.json"
SHEET_NAME = "BotData"

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)

# ---------- Apollo Mock Search Function ----------

MOCK_API_URL = "https://687e15c0c07d1a878c3135af.mockapi.io/people"  # Replace with your real MockAPI endpoint

def search_apollo(query):
    try:
        response = requests.get(MOCK_API_URL)
        response.raise_for_status()
        people = response.json()
        results = []

        for person in people:
            if query.lower() in person["name"].lower():
                result = {
                    "Name": person["name"],
                    "Title": person["title"],
                    "Company": person["company"],
                    "Email": person["email"],
                    "LinkedIn": person["linkedin"]
                }
                results.append(result)

        return results[0] if results else {
            "Name": query,
            "Title": "Not found",
            "Company": "Not found",
            "Email": "Not found",
            "LinkedIn": "Not found"
        }
    except Exception as e:
        print("API error:", e)
        return {
            "Name": query,
            "Title": "Error",
            "Company": "Error",
            "Email": "Error",
            "LinkedIn": "Error"
        }


# ---------- Google Sheets Logging ----------
def log_to_sheet(prompt, result_dict):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet("Sheet1")
    sheet.append_row([datetime.now().isoformat(), prompt, str(result_dict)])

# ---------- /start Command ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Apollo Lookup Bot!\n\nSend a name (text or voice) and I’ll fetch details.")

# ---------- Text Handler ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    result = search_apollo(query)

    reply = f"🔍 *Search Result for:* `{query}`\n\n"
    for key, value in result.items():
        reply += f"*{key}:* {value}\n"

    await update.message.reply_markdown(reply)
    log_to_sheet(query, result)

# ---------- Voice Handler ----------
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    await file.download_to_drive("voice.ogg")

    # Convert to WAV
    sound = AudioSegment.from_ogg("voice.ogg")
    sound.export("voice.wav", format="wav")

    # Transcribe
    recognizer = sr.Recognizer()
    with sr.AudioFile("voice.wav") as source:
        audio = recognizer.record(source)
        try:
            query = recognizer.recognize_google(audio, language="en-IN")
            await update.message.reply_text(f"🗣 You said: *{query}*", parse_mode="Markdown")
            result = search_apollo(query)

            reply = f"🔍 *Search Result for:* `{query}`\n\n"
            for key, value in result.items():
                reply += f"*{key}:* {value}\n"

            await update.message.reply_markdown(reply)
            log_to_sheet(query, result)

        except sr.UnknownValueError:
            await update.message.reply_text("❌ Could not understand the audio.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")

# ---------- Main App ----------
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
