import re
from datetime import datetime
from random import choice
from time import sleep

import requests
import tweepy

from api_keys import *
from categories import *

def run():

    print("Running shakespeare-bot.py at", str(datetime.now()))

    # generate the text string to tweet with very lazy error handling – if anything goes wrong, just try again
    generating = True
    while(generating):
        try:
            place_data = generatePlace()
            text = "‘" + choice(shakespeare_plays) + "’, but set at the " + formatLocation(place_data) + "."
            generating = False
        except Exception as e:
            print("Error:",e)
            print("Trying again…")
            sleep(5)
    
    print(text)
    #sendTweet(text)       # uncomment to activate Twitter
    print("Finished.")

# search for a random business in a random location; it is crucial to pass the location into the API
# as latitude/longitude in order to bias the search properly, otherwise USA results dominate, even if
# a different country is specifically included within the search term
def generatePlace():

    business_type = choice(google_business_categories)
    location = choice(list(places.keys()))
    latlng = places[location]

    print("Searching for:",business_type.strip(),"in",location)

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = dict(
        key = maps_api_key,
        input = business_type.strip() + " in " + location,
        inputtype = "textquery",
        fields = "name,geometry",
        locationbias = "point:" + str(latlng["lat"]) + "," + str(latlng["lng"]),
        language = "en"
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()

    if len(data["candidates"]) > 0:
        return {
            "business_type": business_type,
            "data": data["candidates"][0]
        }
    else:
        print("No results found. Trying again…")
        return generatePlace()

# tidy the format of the place + business description and avoid repetitions
def formatLocation(place_data):

    # set name (=output first item), city and type of business variables
    output = place_data["data"]["name"].strip()
    city = findCity(place_data["data"]["geometry"]["location"])

    # provide the business type with the correct case
    # leading " " identifies items with acronyms or sensitive capitalization that would be removed by .lower()
    business_type = ""
    if place_data["business_type"][0] == " ":
        business_type = place_data["business_type"].strip()
    else:
        business_type = place_data["business_type"].lower()

    # correct apostrophe styles first (as they can affect trimming operations)
    output = tidyInvertedCommas(output)
    city = tidyInvertedCommas(city)
    business_type = tidyInvertedCommas(business_type)

    # remove leading "The" in business names if necessary
    if output[0:4] == "The ":
        output = output[4:]
    
    # remove "restaurant" tag in business names if necessary
    if output[-11:].lower() == " restaurant":
        output = output[:-10]

    # if the name is fully contained in the business type, drop the proper name entirely
    if output.lower() in business_type.lower():
        output = business_type

    # check for business types that repeat elements of the name; do not add type if repeated
    if business_type.lower() not in output.lower():
        output += " " + business_type
    
    # check for place names being repeated within the business name
    if city != "NOT FOUND" and city.lower() not in output.lower():
        output += " in " + city

    return output

# find the city based on the latitude/longitude of the address
def findCity(latlng):

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = dict(
        key = maps_api_key,
        latlng = str(latlng["lat"]) + "," + str(latlng["lng"])
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()

    for component in data["results"][0]["address_components"]:
        if "locality" in component["types"]:
            return component["long_name"]
    return "NOT FOUND"                     # if no "locality" was found

# tidy up any non-smart apostrophes, etc.
def tidyInvertedCommas(input):
    text = re.sub(r"^\"","“",input)     # opening inverted commas at beginning
    text = re.sub(r"\s\""," “",text)    # opening inverted commas in middle
    text = re.sub(r"\"","”",text)       # remaining closing inverted commas
    text = re.sub(r"^\'","‘",text)      # opening single commas at beginning
    text = re.sub(r"\s\'"," ‘",text)    # opening single commas in middle
    text = re.sub(r"\'","’",text)       # remaining closing single commas + apostrophes
    return text

def sendTweet(text):

    # authenticate and set up the Twitter bot
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        twitter = tweepy.API(auth)
    except Exception as e:
        print("Error authenticating with Twitter:",e)
    
    # send the tweet
    try:
        twitter.update_status(status=text)
        print("Tweet sent successfully!")
    except Exception as e:
        print("Error posting tweet:",e)

run()