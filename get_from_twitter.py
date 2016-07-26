import tweepy

import os
import settings

# Make a settings.py file in this directory that looks as follows --
# import os
# os.environ['CONSUMER_TOKEN'] = '##########################'
# os.environ['CONSUMER_SECRET'] = '##########################'
# os.environ['ACCESS_TOKEN'] = '##########################'
# os.environ['ACCESS_TOKEN_SECRET'] = '##########################'

auth = tweepy.OAuthHandler(os.environ['CONSUMER_TOKEN'], os.environ['CONSUMER_SECRET'])
auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

query = 'homeless SF OR San Francisco'
max_tweets = 1000

import csv

with open('sfhomeless.csv', 'w') as csvfile:
    fieldnames = ['index', 'text', 'created_at', 'retweet_count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    results_count = 0
    for result in tweepy.Cursor(api.search, q=query).items(max_tweets):
        writer.writerow({
        'index': results_count,
        'text': result.text.encode('utf-8'),
        'created_at': result.created_at,
        'retweet_count': len(api.retweets(result.id))
        })
        results_count += 1
        print("Reached " + str(results_count) + " results.")
