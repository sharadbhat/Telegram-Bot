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


#methods

#Method called when the bot is started
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello " + str(update.message.from_user.first_name) + ",\nThis is your assisstant.")
    bot.send_message(chat_id=update.message.chat_id, text="Type /help for more information.")


#Help Text. "/help"
def helpText(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="For a quote, reply with /quote")
    bot.send_message(chat_id=update.message.chat_id, text="For a joke, reply with /joke")
    bot.send_message(chat_id=update.message.chat_id, text="For a comic, reply with /comic")
    bot.send_message(chat_id=update.message.chat_id, text="For the weather, reply with -\n/weather <cityname>\n\nExample:\n/weather bangalore")
    bot.send_message(chat_id=update.message.chat_id, text="For an image, reply with -\n/image <portrait/landscape/square>\n\nExample:\n/image portrait")
    bot.send_message(chat_id=update.message.chat_id, text="For a random fact, reply with /fact")
    bot.send_message(chat_id=update.message.chat_id, text="For a video, reply with /video <name>\n\nExample: /video Daft Punk Get Lucky")
    bot.send_message(chat_id=update.message.chat_id, text="For definition of a word, reply with -\n/define <word>\n\nExample:\n/define ostentatious")
    bot.send_message(chat_id=update.message.chat_id, text="For restaurants in an area, reply with -\n/restaurants <area name>\n\nExample:\n/restaurants koramangala")


#Fetches a random comic from xkcd. "/comic"
def sendComic(bot, update):
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


#Returns weather of the place. "/weather bangalore"
def sendWeather(bot, update, args):
    try:
        #args = "new", "York"
        apiKey = "***********************"
        citySendToAPI = ''.join(args).lower() #newyork
        city = ' '.join(args).lower() #new york
        r = (requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + citySendToAPI + "&APPID=" + apiKey + "&units=metric").content).decode("utf-8")
        a = ast.literal_eval(r)
        weather = (a["weather"][0]["description"]).capitalize()
        temperature = str(a["main"]["temp"]) + "°C"
        humidity = str(a["main"]["humidity"]) + "%"
        wind = str(a["wind"]["speed"]) + "km/h"
        cityFound = str(a["name"]) #New York
        cityGotFromAPI = str(a["name"]).lower() #new york
        if city == cityGotFromAPI:
            city = cityFound + ", " + str(a["sys"]["country"])
            bot.send_message(chat_id=update.message.chat_id, text="Here is the weather in " + city)
            bot.send_message(chat_id=update.message.chat_id, text=("*" + city + "*\n\nWeather: " + weather + "\nTemperature: " + temperature + "\nHumidity: " + humidity + "\nWind: " + wind), parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="City not found")
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching weather")


#Returns the definition and example of a word. "/define word"
def sendDefinition(bot, update, args):
    word = ' '.join(args).capitalize()
    definition, example = defineWord(word, bot, update)
    if definition != "" and example != "":
        bot.send_message(chat_id=update.message.chat_id, text=("*" + word + "*\n" + definition + "\n\n_Example_\n" + example), parse_mode=telegram.ParseMode.MARKDOWN)


#Returns a random joke from the icanhazdadjoke API. "/joke"
def sendJoke(bot, update):
    try:
        headers = {'Accept': 'application/json'}
        r = (requests.get("https://icanhazdadjoke.com", headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)
        bot.send_message(chat_id=update.message.chat_id, text="Here is your joke, "+ str(update.message.from_user.first_name))
        bot.send_message(chat_id=update.message.chat_id, text=a["joke"])
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching joke")


#Returns the YouTube URL of the first video. "/video Daft Punk Get Lucky"
def sendVideoURL(bot, update, args):
    try:
        textToSearch = args
        query = '+'.join(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            videoURL = ('https://www.youtube.com' + vid['href'])
            break
        bot.send_message(chat_id=update.message.chat_id, text=videoURL)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching video URL.")


#Returns a list of restaurants and cuisines
def restaurantsAroundMe(bot, update, args):
    try:
        if len(args) == 0:
            bot.send_message(chat_id=update.message.chat_id, text="Please type location name.\n/restaurants area name")
        else:
            areaName = '%20'.join(args)
            headers = {'Accept': 'application/json', 'user-key': '*******************'}
            r = (requests.get("https://developers.zomato.com/api/v2.1/search?q=" + areaName, headers=headers).content).decode("utf-8")
            a = ast.literal_eval(r)
            count = 0
            area = a["restaurants"][0]["restaurant"]["location"]["locality"]
            text = ""
            for i in a["restaurants"]:
                count += 1
                link = str(i["restaurant"]["url"]).replace("\\","")
                name = i["restaurant"]["name"]
                text = text + "*" + name + "*"
                text = text + "\nAverage Rating: " + str(i["restaurant"]["user_rating"]["aggregate_rating"])
                text = text + "\nCuisines: " + i["restaurant"]["cuisines"]
                text = text + "\nAverage Cost for 2: " + i["restaurant"]["currency"] + " " + str(i["restaurant"]["average_cost_for_two"])
                text = text + "\n[" + name + "](" + str(link) + ")"
                if count == 5:
                    break
                text = text + "\n\n"
            bot.send_message(chat_id=update.message.chat_id, text="Here are the restaurants around " + area)
            bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching restaurants.")


#Returns a random quote from the forismatic API. "/quote"
def sendQuote(bot, update):
    try:
        a = (requests.get('http://api.forismatic.com/api/1.0/?method=getQuote&key=453&format=json&lang=en').content).decode("utf-8")
        a = ast.literal_eval(a)
        bot.send_message(chat_id=update.message.chat_id, text="Here is your quote, "+ str(update.message.from_user.first_name))
        bot.send_message(chat_id=update.message.chat_id, text=(a['quoteText'] + "\n\n- " + a['quoteAuthor']))
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching quote")


#Returns the message sent to it.
def echo(bot, update):
    try:
        inputQuery = update.message.text
        request = ai.text_request()
        request.lang = 'en'
        request.query = inputQuery
        response = request.getresponse()
        responsestr = response.read().decode('utf-8')
        response_obj = json.loads(responsestr)
        reply = response_obj["result"]["fulfillment"]["speech"]
        bot.send_message(chat_id=update.message.chat_id, text=reply)
    except:
        bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


#Returns "Unknown Command" if the command is not recognized.
def unknownCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I did not understand that command.")


#Returns a random fact from the numbersapi API. "/fact"
def sendNumberFact(bot, update):
    try:
        a = (requests.get('http://numbersapi.com/random/trivia').content).decode("utf-8")
        bot.send_message(chat_id=update.message.chat_id, text="Here is your fact, "+ str(update.message.from_user.first_name))
        bot.send_message(chat_id=update.message.chat_id, text=a)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error in fetching fact")


#Returns an image based on orientation. "/image <orientation>"
def sendImage(bot, update, args):
    try:
        orientation = ' '.join(args).lower()
        downloadImage(bot, update, orientation)
        bot.send_photo(chat_id=update.message.chat_id, photo=open('image.jpg', 'rb'))
        os.remove('image.jpg')
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Error")


#Downloads the image from unsplash.
def downloadImage(bot, update, orientation):
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


#Gets the definition from Oxford Dictionary API.
def defineWord(wordID, bot, update):
    appID = '********'
    appKey = '********************'
    language = 'en'
    if wordID == "":
        bot.send_message(chat_id=update.message.chat_id, text="Please enter a word after the /define command")
        return "", ""
    try:
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + wordID.lower()
        r = requests.get(url, headers = {'app_id': appID, 'app_key': appKey})
        jsonText = str(r.text)
        jsonText = ast.literal_eval(jsonText)
        completeDefinition = str(jsonText['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]) + "."
        completeExample = str(jsonText['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['examples'][0]['text']) + "."
    except:
        return "Not Available", "Not Available"
    return completeDefinition.capitalize(), completeExample.capitalize()


#handlers
startHandler = CommandHandler('start', start)
helpHandler = CommandHandler('help', helpText)
weatherHandler = CommandHandler('weather', sendWeather, pass_args=True)
factHandler = CommandHandler('fact', sendNumberFact)
comicHandler = CommandHandler('comic', sendComic)
restaurantHandler = CommandHandler('restaurants', restaurantsAroundMe, pass_args=True)
videoURLHandler = CommandHandler('video', sendVideoURL, pass_args=True)
jokeHandler=  CommandHandler('joke', sendJoke)
definitionHandler = CommandHandler('define', sendDefinition, pass_args=True)
quoteHandler = CommandHandler('quote', sendQuote)
imageHandler = CommandHandler('image', sendImage, pass_args=True)
echoHandler = MessageHandler(Filters.text, echo)
unknownHandler = MessageHandler(Filters.command, unknownCommand)

#adding handlers to dispatcher
dispatcher.add_handler(startHandler)
dispatcher.add_handler(imageHandler)
dispatcher.add_handler(weatherHandler)
dispatcher.add_handler(comicHandler)
dispatcher.add_handler(restaurantHandler)
dispatcher.add_handler(videoURLHandler)
dispatcher.add_handler(helpHandler)
dispatcher.add_handler(definitionHandler)
dispatcher.add_handler(jokeHandler)
dispatcher.add_handler(factHandler)
dispatcher.add_handler(quoteHandler)
dispatcher.add_handler(echoHandler)
dispatcher.add_handler(unknownHandler)


updater.start_polling()
