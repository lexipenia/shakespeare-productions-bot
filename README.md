# shakespeare-bot

This bot generates contemporary Shakespeare productions by using the Google Maps API to find random places and [posts them to Twitter](https://twitter.com/allzeworld).

It searches a list of business categories used by Google that I found [here](https://pixelcutlabs.com/blog/google-my-business-categories/), looking for them all over the world. I had to prune the list somewhat to make these categories fit the tweets grammatically, and still may not have been wholly successful in doing so.

I found that to get Google Maps to return results from countries around the world, I had to bias the search using their latitude/longitude. Just entering the country name in the search term did not seem to have much effect, and the majority of results returned were in the USA.

## API keys

If you want to run this bot without connecting it to Twitter, you will still need a Google Maps API key. At present, you must set up a billing account with Google to get one. However, you won't be charged for using the API if you're not doing anything heavy-duty with it. There's a $200 credit available every month.

You'll need to create a file in the same directory as the bot called `api_keys.py` with the following format:

```
# put your Google Maps API key here
maps_api_key = ""

# put your Twitter API keys here
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
```

## Dependencies
```
pip install requests tweepy
```