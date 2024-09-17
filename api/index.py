from fastapi import FastAPI, Request
from telebot.types import Update
import telebot
import sys
import os

# הוסף את הנתיב של התיקייה הראשית לPYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import bot, handle_photo

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    json_string = await request.json()
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return ""

@app.get("/")
async def root():
    return {"message": "הבוט פעיל!"}