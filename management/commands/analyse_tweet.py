from django.core.management.base import BaseCommand, CommandError
import os
import requests
import json
from datetime import datetime
from time import sleep
from django.utils.dateparse import parse_date
from django.utils.text import Truncator
from waybackpy import WaybackMachineSaveAPI
from polls.models import *

bearer_token = os.environ.get("BEARER_TOKEN_CONSOLE")

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    label_name = ''
    next_token = ''
    tweet_id = '1590440317362515968'

    def add_arguments(self, parser):
        parser.add_argument('tweet_id', nargs='+', type=int)
        parser.add_argument('backup', nargs='+', type=int)

    def handle(self, *args, **options):

        self.fire(options['tweet_id'][0])

        self.stdout.write(self.style.SUCCESS('Successfully closed Tweet'))

    def tweetLikes(self, id):
        user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        url = "https://api.twitter.com/2/tweets/{}/liking_users?max_results=100".format(id)
        return url, user_fields

    def tweetRead(self, id):
        tweet_fields = "tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld"
        url = "https://api.twitter.com/2/tweets/{}".format(id)
        return url, tweet_fields

    def userRead(self, id):
        user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        url = "https://api.twitter.com/2/users/{}".format(id)
        return url, user_fields

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2LikingUsersPython"
        return r

    def exitIfNotAuthorized(self, json_response):
        try:
            if 'errors' in json_response:
                print(json_response)
                return True
        except:
            return True
        return False

    def connect_to_endpoint(self, url, user_fields, id):
        response = requests.request("GET", url, auth=self.bearer_oauth, params=user_fields)
        if response:
            if response.status_code != 200:
                print('Too many requests, wait 5 minutes')
                sleep(300)
                self.fire(id)
            else:
                return response.json()
        else:
            print('Too many requests, wait 5 minutes')
            sleep(300)
            self.fire(id)

    def fire(self, id):
        tweets_counter = 0
        url, tweet_fields = self.tweetLikes(id)
        json_response = self.connect_to_endpoint(url, tweet_fields, id)

        try:
            if 'errors' in json_response:
                print(json_response['errors'])
                pass
            else:
                tweets_counter += json_response["meta"]["result_count"]
        except:
            pass


        if self.exitIfNotAuthorized(json_response):
            return 2

        count = 0
        user_exist = 0
        user_not_exist = 0
        default_profile = 0
        followers_count = 0
        health_index = 0
        for item in json_response['data']:
            user = Users.objects.filter(user_id=json_response['data'][count]['id']).values()

            if(item['profile_image_url'] == 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png'):
                default_profile += 1

            if item['public_metrics']['followers_count'] >= 50:
                followers_count += 1
            if(user):
                user_exist += 1
            else:
                user_not_exist += 1
            count += 1
        
        analyse_result = user_exist/(user_exist+user_not_exist)*100

        health_index = round((100-analyse_result)/10)

        print(analyse_result, health_index)

        return 0
        try:
            statusFile = open("analyse-status.csv", "r")
            self.next_token = eval(statusFile.read())['next_token']
            if self.next_token:
                json_response["meta"]["next_token"] = self.next_token
        except FileNotFoundError:
            print('Status file does not exists.')

        statusFile = open("analyse-status.csv", "w")
        statusFile.write(str(json_response["meta"]))
        statusFile.close()

        while json_response["meta"]["next_token"]:

            tweets_counter += json_response["meta"]["result_count"]

            sleep(1)

            if json_response['meta']['result_count'] != 0:
                json_response = self.connect_to_endpoint(url + '&pagination_token=' + json_response["meta"]["next_token"], tweet_fields, id)
            else:
                break    

            try:
                json_response["meta"]
                json_response["data"]

                if json_response['meta']['result_count'] == 0:
                    break
            except:
                break

            statusFile = open("analyse-status.csv", "w")
            statusFile.write(str(json_response["meta"]))
            statusFile.close()

        try:
            os.remove("analyse-status.csv")
        except:
            print('analyse-status.csv not found.')
            pass

        print("Total like counter:" + str(tweets_counter))

