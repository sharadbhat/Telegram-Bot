from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
import logging
import telegram
import os.path
import sys
import json
import requests
import ast
import string
import os
import ast
import urllib.parse
import urllib.request
import bs4
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

updater = Updater(token='***********************************')

CLIENT_ACCESS_TOKEN = '*****************'
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


#Command Functionss

def start(bot, update):
    """
    Method called when the bot is started
    """
    bot.send_message(chat_id=update.message.chat_id, text="Hello " + str(update.message.from_user.first_name) + ",\nThis is your assisstant.")
    bot.send_message(chat_id=update.message.chat_id, text="Type /help for more information.")


def help_text(bot, update):
    """
    Help Text.
    "/help"
    """
    bot.send_message(chat_id=update.message.chat_id, text="For a quote, reply with /quote")
    bot.send_message(chat_id=update.message.chat_id, text="For a joke, reply with /joke")
    bot.send_message(chat_id=update.message.chat_id, text="For a comic, reply with /comic")
    bot.send_message(chat_id=update.message.chat_id, text="For the weather, reply with -\n/weather <cityname>\n\nExample:\n/weather bangalore")
    bot.send_message(chat_id=update.message.chat_id, text="For an image, reply with -\n/image <portrait/landscape/square>\n\nExample:\n/image portrait")
    bot.send_message(chat_id=update.message.chat_id, text="For a random fact, reply with /fact")
    bot.send_message(chat_id=update.message.chat_id, text="For a video, reply with /video <name>\n\nExample: /video Daft Punk Get Lucky")
    bot.send_message(chat_id=update.message.chat_id, text="For definition of a word, reply with -\n/define <word>\n\nExample:\n/define ostentatious")
    bot.send_message(chat_id=update.message.chat_id, text="For restaurants in an area, reply with -\n/restaurants <area name>\n\nExample:\n/restaurants koramangala")


def send_quote(bot, update):
    """
    Returns a random quote from the forismatic API.
    "/quote"
    """
    try:
        a = (requests.get('http://api.forismatic.com/api/1.0/?method=getQuote&key=453&format=json&lang=en').content).decode("utf-8")
        a = ast.literal_eval(a)
        bot.send_message(chat_id=update.message.chat_id, text="Here is your quote, "+ str(update.message.from_user.first_name))
        bot.send_message(chat_id=update.message.chat_id, text=(a['quoteText'] + "\n\n- " + a['quoteAuthor']))
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching quote")


def send_joke(bot, update):
    """
    Returns a random joke from the icanhazdadjoke API.
    "/joke"
    """
    try:
        headers = {'Accept': 'application/json'}
        r = (requests.get("https://icanhazdadjoke.com", headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)
        bot.send_message(chat_id=update.message.chat_id, text="Here is your joke, "+ str(update.message.from_user.first_name))
        bot.send_message(chat_id=update.message.chat_id, text=a["joke"])
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching joke")


def send_comic(bot, update):
    """
    Fetches a random comic from xkcd.
    "/comic"
    """
    try:
        r = requests.get("https://c.xkcd.com/random/comic/")
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        count = 0
        for img in soup.find_all('img'):
            url = "http:" + str(img.get('src'))
            title = img.get('title')
            if count == 1:
                break
            count = 1
        bot.send_message(chat_id=update.message.chat_id, text="Here is the comic.")
        bot.send_photo(chat_id=update.message.chat_id, photo=url)
        bot.send_message(chat_id=update.message.chat_id, text=title)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching comic")


def send_weather(bot, update, args):
    """
    Returns weather of the place.
    "/weather bangalore"
    """
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Enter city name. /weather <city name>")
    try:
        #args = "new", "York"
        API_KEY = "***********************"
        city_sent_to_API = ''.join(args).lower() #newyork
        city = ' '.join(args).lower() #new york
        r = (requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city_sent_to_API + "&APPID=" + API_KEY + "&units=metric").content).decode("utf-8")
        a = ast.literal_eval(r)
        weather = (a["weather"][0]["description"]).capitalize()
        temperature = str(a["main"]["temp"]) + "°C"
        humidity = str(a["main"]["humidity"]) + "%"
        wind = str(a["wind"]["speed"]) + "km/h"
        city_found = str(a["name"]) #New York
        city_got_from_API = str(a["name"]).lower() #new york
        if city == city_got_from_API:
            city = city_found + ", " + str(a["sys"]["country"])
            bot.send_message(chat_id=update.message.chat_id, text="Here is the weather in " + city)
            bot.send_message(chat_id=update.message.chat_id, text=("*" + city + "*\n\nWeather: " + weather + "\nTemperature: " + temperature + "\nHumidity: " + humidity + "\nWind: " + wind), parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="City not found")
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching weather")


def send_image(bot, update, args):
    """
    Returns an image based on orientation.
    "/image <orientation>"
    """
    try:
        orientation = ' '.join(args).lower()
        download_image(bot, update, orientation)
        bot.send_photo(chat_id=update.message.chat_id, photo=open('image.jpg', 'rb'))
        os.remove('image.jpg')
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error")


def send_number_fact(bot, update):
    """
    Returns a random fact from the numbersapi API.
    "/fact"
    """
    try:
        a = (requests.get('http://numbersapi.com/random/trivia').content).decode("utf-8")
        bot.send_message(chat_id=update.message.chat_id, text="Here is your fact, "+ str(update.message.from_user.first_name))
        bot.send_message(chat_id=update.message.chat_id, text=a)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching fact")


def send_video_URL(bot, update, args):
    """
    Returns the YouTube URL of the first video.
    "/video Daft Punk Get Lucky"
    """
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Enter video name. /video <video name>")
    try:
        text_to_search = args
        query = '+'.join(text_to_search)
        url = "https://www.youtube.com/results?search_query=" + query
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            videoURL = ('https://www.youtube.com' + vid['href'])
            break
        bot.send_message(chat_id=update.message.chat_id, text=videoURL)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching video URL.")


def send_definition(bot, update, args):
    """
    Returns the definition and example of a word.
    "/define word"
    """
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Enter word. /define <word>")
    word = ' '.join(args).capitalize()
    definition, example = define_word(word, bot, update)
    if definition != "" and example != "":
        bot.send_message(chat_id=update.message.chat_id, text=("*" + word + "*\n" + definition + "\n\n_Example_\n" + example), parse_mode=telegram.ParseMode.MARKDOWN)


def send_restaurants_list(bot, update, args):
    """
    Returns a list of restaurants and cuisines
    "/restaurants JP Nagar"
    """
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Please type location name.\n/restaurants area name")
    try:
        area_name = '%20'.join(args)
        USER_KEY = '*****************'
        headers = {'Accept': 'application/json', 'user-key': USER_KEY}
        r = (requests.get("https://developers.zomato.com/api/v2.1/search?q=" + area_name, headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)
        count = 0
        area = a["restaurants"][0]["restaurant"]["location"]["locality"]
        for i in a["restaurants"]:
            count += 1
            link = str(i["restaurant"]["url"]).replace("\\","")
            name = i["restaurant"]["name"]
            text = "*" + name + "*"
            text += "\nAverage Rating: " + str(i["restaurant"]["user_rating"]["aggregate_rating"])
            text += "\nCuisines: " + i["restaurant"]["cuisines"]
            text += "\nAverage Cost for 2: " + i["restaurant"]["currency"] + " " + str(i["restaurant"]["average_cost_for_two"])
            text += "\n[" + name + "](" + str(link) + ")"
            if count == 5:
                break
            text += "\n\n"
        bot.send_message(chat_id=update.message.chat_id, text="Here are the restaurants around " + area)
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching restaurants.")


def small_talk(bot, update):
    """
    Small talk using api.ai
    """
    try:
        input_query = update.message.text
        request = ai.text_request()
        request.lang = 'en'
        request.query = input_query
        response = request.getresponse()
        responsestr = response.read().decode('utf-8')
        response_obj = json.loads(responsestr)
        reply = response_obj["result"]["fulfillment"]["speech"]
        bot.send_message(chat_id=update.message.chat_id, text=reply)
    except:
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def unknown_command(bot, update):
    """
    Returns "Unknown Command" if the command is not recognized.
    """
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I did not understand that command.")



#Helper Functions

def download_image(bot, update, orientation):
    """
    Downloads the image from unsplash.
    """
    try:
        f = open('image.jpg','wb')
        if orientation == 'portrait':
            f.write(requests.get('https://unsplash.it/1080/1920/?random').content)
        elif orientation == 'landscape':
            f.write(requests.get('https://unsplash.it/1920/1080/?random').content)
        else:
            f.write(requests.get('https://unsplash.it/500/?random').content)
        f.close()
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching image")


def define_word(word_ID, bot, update):
    """
    Gets the definition from Oxford Dictionary API.
    """
    APP_ID = '********'
    APP_KEY = '********************'
    language = 'en'
    try:
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_ID.lower()
        r = requests.get(url, headers = {'app_id': APP_ID, 'app_key': APP_KEY})
        json_text = str(r.text)
        json_text = ast.literal_eval(json_text)
        complete_definition = str(json_text['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]) + "."
        complete_example = str(json_text['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['examples'][0]['text']) + "."
    except:
        return "Not Available", "Not Available"
    return complete_definition.capitalize(), complete_example.capitalize()



#handlers
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help_text)
quote_handler = CommandHandler('quote', send_quote)
joke_handler =  CommandHandler('joke', send_joke)
comic_handler = CommandHandler('comic', send_comic)
weather_handler = CommandHandler('weather', send_weather, pass_args=True)
image_handler = CommandHandler('image', send_image, pass_args=True)
fact_handler = CommandHandler('fact', send_number_fact)
video_URL_handler = CommandHandler('video', send_video_URL, pass_args=True)
definition_handler = CommandHandler('define', send_definition, pass_args=True)
restaurant_handler = CommandHandler('restaurants', send_restaurants_list, pass_args=True)
small_talk_handler = MessageHandler(Filters.text, small_talk)
unkown_handler = MessageHandler(Filters.command, unknown_command)



#adding handlers to dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(quote_handler)
dispatcher.add_handler(joke_handler)
dispatcher.add_handler(comic_handler)
dispatcher.add_handler(weather_handler)
dispatcher.add_handler(image_handler)
dispatcher.add_handler(fact_handler)
dispatcher.add_handler(video_URL_handler)
dispatcher.add_handler(definition_handler)
dispatcher.add_handler(restaurant_handler)
dispatcher.add_handler(small_talk_handler)
dispatcher.add_handler(unkown_handler)



updater.start_polling()
