from django.core.management.base import BaseCommand, CommandError
import tweepy
import os
import requests
import json
from time import sleep
from django.utils.dateparse import parse_date
from django.utils.text import Truncator
from waybackpy import WaybackMachineSaveAPI
from polls.models import *
import redis
import time
import datetime

bearer_token=os.environ.get("BEARER_TOKEN_WEB")
redis_password=os.environ.get("REDIS_PASS")

class Command(BaseCommand):
    help = 'Archive the tweets'
    next_token = ''

    def handle(self, *args, **options):
        self.fire()
        self.stdout.write(self.style.SUCCESS('Tweet has been successfully archived!'))

    def mentionRead(self):
        time = datetime.datetime.now() - datetime.timedelta(minutes=15)
        start_time = time.strftime('%Y-%m-%dT%H:%M:00.000Z')
        print(start_time)
        user_fields = "user.fields=id;tweet.fields=referenced_tweets"
        url = "https://api.twitter.com/2/users/{}/mentions?start_time={}".format(os.environ.get("ADMIN_USER"), start_time)
        return url, user_fields

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2LikingUsersPython"
        return r


    def connect_to_endpoint(self, url, user_fields, method):
        response = requests.request(method, url, auth=self.bearer_oauth, params=user_fields)
        return response.text

    def fire(self):
        url, tweet_fields = self.mentionRead()
        json_response = json.loads(self.connect_to_endpoint(url, tweet_fields, 'GET'))
        if json_response['meta']['result_count']:
            for tweet in json_response['data']:
                if ((tweet['text'].find('@1500life') != -1 or tweet['text'].find('@1500Life') != -1)):
                    if (tweet['text'].find('آرشیو') != -1):
                        if 'referenced_tweets' in tweet:
                            redisClient = redis.Redis(password=redis_password)

                            if redisClient.get(tweet['id']) == None:
                                print('Internet Archive')
                                internet_archive_result = ''
                                url = 'https://twitter.com/twitter/status/' + tweet['referenced_tweets'][0]['id']
                                user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
                                save_api = WaybackMachineSaveAPI(url, user_agent)
                                try:
                                    internet_archive_result = save_api.save()
                                except:
                                    print('error during archiving')
                                    exit

                                print('Internet Archive status: ' + str(internet_archive_result))

                                print('Send reply')
                                message = "توییت مورد نظر در وبسایت اینترنت آرکایو در این لحظه آرشیو شد: {} \n\n نتایج این آرشیو توسط یک بات توییتری ارسال شده است 🤖 ".format(internet_archive_result)
                                self.sendReply(message, tweet['id'])

                                redisClient.set(tweet['id'], 0)
                            else:
                                print('The queue is empty!')

    def sendReply(self, message, tweet_id):
        twitter_auth_keys = {
            "consumer_key"        : os.environ.get("CONSUMER_KEY_WEB"),
            "consumer_secret"     : os.environ.get("CONSUMER_SECRET_WEB"),
            "access_token"        : os.environ.get("ACCESS_TOKEN_WEB"),
            "access_token_secret" : os.environ.get("ACCESS_TOKEN_SECRET_WEB")
        }
    
        auth = tweepy.OAuthHandler(
                twitter_auth_keys['consumer_key'],
                twitter_auth_keys['consumer_secret']
                )
        auth.set_access_token(
                twitter_auth_keys['access_token'],
                twitter_auth_keys['access_token_secret']
                )
        api = tweepy.API(auth)
    
        status = api.update_status(status=message, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
 
    