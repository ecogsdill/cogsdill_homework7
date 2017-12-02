# Dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import tweepy
from textblob import TextBlob, Word, Blobber
import time
import os

# Initialize Sentiment Analyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# Twitter API Keys
consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


#set up a list to store the names of already mentioned users
user_mentions=[]

#The self_user is me.
self_user='@ecogsdill_HA'


#Retrieve a list of distinct mentioned users who have not already been analyzed in the past 500 tweets

def RetrieveNewMentionedUsers(self_user):
    
    new_mentions=[]
    
    for i in range (0, 25): #look through most recent 500 tweets

        public_tweets = api.user_timeline(self_user,page=i)
       
        for tweet in public_tweets:
            if len(tweet['entities']['user_mentions'])>0 and tweet['entities']['user_mentions'][0]['screen_name'] not in user_mentions and tweet['entities']['user_mentions'][0]['screen_name'] not in new_mentions:
                new_mentions.append(tweet['entities']['user_mentions'][0]['screen_name'])

    #add target_user value to this list after it's analyzed
    return new_mentions


def Sentiment100Tweets(target_user):

    sentiments=[]
    pos=[]
    neg=[]
    neu=[]
    compound=[]
    counter=1
    
    # Loop through 5 pages of tweets (total 100 tweets)
    for x in range(5):

        # Get user's tweets
        public_tweets = api.user_timeline(target_user, page=x)

        # Loop through all tweets 
        for tweet in public_tweets:


            # Run Vader Analysis on each tweet
            results = analyzer.polarity_scores(tweet['text'])     

            # Add sentiments for each tweet into an array (as a dictionary)

            sentiments.append({"Tweets Ago":counter,
                               "Date":tweet['created_at'],
                              "Positive":results["pos"],
                              "Negative":results["neg"],
                              "Neutral":results["neu"],
                              "Compound":results["compound"]})

            counter=counter+1
            pos.append(results["pos"])
            neg.append(results["neg"])
            neu.append(results["neu"])
            compound.append(results["compound"])            
            
    
    return sentiments


#this is the actual function that executes every 5 minutes
def updateTwitter():
    
    RetrieveNewMentionedUsers(self_user)

    for user in RetrieveNewMentionedUsers(self_user):
        print(user)
        sentiment=Sentiment100Tweets(user)

        x=[]
        y=[]

        for row in sentiment:
            x.append(row['Tweets Ago'])
            y.append(row['Compound'])

        plt.plot(x,y,marker='o')
        plt.xlabel("Tweets Ago")
        plt.ylabel("Polarity")
        plt.savefig('plot.png')
        plt.show()
        api.update_with_media('plot.png', f"These are {user}'s tweets lol ... RIP")
        user_mentions.append(user)

#while true:

    # Call the TweetQuotes function and specify the tweet number
 #   updateTwitter()

    # Once tweeted, wait 60 seconds before doing anything else
  #  time.sleep(60)


# Create a function that calls the TweetOut function every minute
counter = 1

# Infinitely loop
t_end = time.time() + 60 * 5

while(time.time() < t_end):

    # Call the TweetQuotes function and specify the tweet number
    updateTwitter()

    # Once tweeted, wait 60 seconds before doing anything else
    time.sleep(60)

    # Add 1 to the counter prior to re-running the loop
    counter = counter + 1

