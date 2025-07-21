# A
This Telegram bot helps users find details about people (like name, title, company, email, LinkedIn) using text or voice input.

🚀 How It Works:
User Input (via Telegram):

Sends a text or voice message (in English or Hindi).

Bot Receives Input:

If voice, it gets transcribed using Google Speech Recognition.

If text, it’s sent directly.

Search Logic:

The name is sent to a Mock API (hosted on mockapi.io).

The API returns details if a match is found.

Bot Responds:

It sends a nicely formatted message with:

Name

Title

Company

Email

LinkedIn

Logging:

The bot logs:

Timestamp

Search input

Search result

All data is stored in Google Sheets using the Google Sheets API.

🧰 Tech Stack Used:
Feature	Technology
Bot platform	Telegram Bot API
Bot framework	python-telegram-bot v20+
Voice-to-text	SpeechRecognition, pydub, ffmpeg
Search API	Mock API (via requests)
Data logging	Google Sheets (gspread, oauth2client)
Hosting	Local / Python environment
