import telebot
from telebot import types
import re, os 
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

user_selection = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Video"), types.KeyboardButton("Playlist"))
    bot.reply_to(message, "Welcome to our bot! Please select one:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Video", "Channel", "Playlist"])
def handle_selection(message):
    user_id = message.from_user.id
    user_selection[user_id] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Back"))
    if message.text == "Channel":
        bot.send_message(message.chat.id, "You selected Channel! Please send the URL of the channel.", reply_markup=markup)
    elif message.text == "Playlist":
        bot.send_message(message.chat.id, "You selected Playlist! Please send the URL of the playlist.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"You selected Video! Please send the URL of the video", reply_markup=markup)


def is_valid_channel_url(url):
    return re.match(r'https?://(www\.)?youtube\.com/channel/[a-zA-Z0-9_-]+', url)


def is_valid_playlist_url(url):
    return re.match(r'https?://(www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+', url)


def is_valid_url(url):
    return re.match(r'^https?://', url)


@bot.message_handler(func=lambda message: message.from_user.id in user_selection)
def handle_url(message):
    user_id = message.from_user.id
    selected_type = user_selection.get(user_id)
    url = message.text
    if url == "Back":
        send_welcome(message)
        del user_selection[user_id]
        return
    if selected_type == "Channel" and is_valid_channel_url(url):
        bot.send_message(message.chat.id, f"URL of the channel: {url}")
    elif selected_type == "Playlist" and is_valid_playlist_url(url):
        bot.send_message(message.chat.id, f"URL of the playlist: {url}")
    elif is_valid_url(url):
        bot.send_message(message.chat.id, f"You selected {selected_type}! URL: {url}")
        # Sending request to the API
        api_url = "https://abdirazzokov.pythonanywhere.com/getimage"
        data = {"url": url, "type": selected_type.lower()}
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            bot.send_photo(message.chat.id, photo=response.json()["image"])
        else:
            bot.send_message(message.chat.id, f"Error sending request to API: {response.status_code}")
    else:
        bot.send_message(message.chat.id, "Invalid URL.")

bot.infinity_polling()