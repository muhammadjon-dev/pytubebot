import telebot
from telebot import types
import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

user_selection = {}

def create_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    video_button = types.KeyboardButton("📹 Video")
    playlist_button = types.KeyboardButton("📂 Playlist")
    markup.add(video_button, playlist_button)
    return markup

def create_back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("⏮ Back")
    markup.add(back_button)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = create_main_markup()
    bot.reply_to(message, "Welcome to our bot! Please select one:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["📹 Video", "📂 Playlist"])
def handle_selection(message):
    user_id = message.from_user.id
    user_selection[user_id] = message.text
    markup = create_back_markup()
    if message.text == "📂 Playlist":
        bot.send_message(message.chat.id, "You selected Playlist! Please send the URL of the playlist.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You selected Video! Please send the URL of the video.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⏮ Back")
def handle_back(message):
    send_welcome(message)

def is_valid_url(url):
    return re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)

def is_valid_playlist_url(url):
    match = re.match(r'https?://(www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+', url)
    print(f"Playlist URL validation result for '{url}': {match}")
    return match

def is_valid_video_url(url):
    match = re.match(r'https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+', url)
    print(f"Video URL validation result for '{url}': {match}")
    return match

def process_url(message, selected_type, url):
    api_url = "http://www.pytube.live/getimage"
    data = {
        "url": url,
        "type": "playlist" if selected_type == "📂 Playlist" else "video"
    }
    try:
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if "image" in response_data:
                bot.send_photo(message.chat.id, photo=response_data["image"], caption="@ytubepy_bot")
            else:
                bot.send_message(message.chat.id, "The API did not return an image.")
        else:
            error_msg = response["error"]
            bot.send_message(message.chat.id, f"Error sending request to API: {error_msg}")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"Request failed: {str(e)}")

@bot.message_handler(func=lambda message: message.from_user.id in user_selection)
def handle_url(message):
    user_id = message.from_user.id
    selected_type = user_selection.get(user_id)
    url = message.text

    if url == "⏮ Back":
        del user_selection[user_id]
        handle_back(message)
    elif selected_type == "📂 Playlist":
        if is_valid_playlist_url(url):
            process_url(message, selected_type, url)
        else:
            bot.send_message(message.chat.id, "Invalid playlist URL. Please send a valid YouTube playlist URL.")
    elif selected_type == "📹 Video":
        if is_valid_video_url(url):
            process_url(message, selected_type, url)
        else:
            bot.send_message(message.chat.id, "Invalid video URL. Please send a valid YouTube video URL.")
    else:
        bot.send_message(message.chat.id, "Invalid URL.")

bot.infinity_polling()