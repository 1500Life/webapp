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
    next_token = ''
    tweet_archive = ''
    tweet_details = []
    analytics = []

    def handle(self, *args, **options):

        tweet_id = '1611939099967115272'

        self.fire(tweet_id)

        self.analytics = sorted(self.analytics, key=lambda user: user[0])

        print(self.analytics)
        for i in self.analytics:
            statusFile = open("data/analytics-report-{}.txt".format(tweet_id), "a+")
            statusFile.write(str(i)+'\n')
            statusFile.close()
            print(i)

        self.stdout.write(self.style.SUCCESS('Successfully Analysed Tweet'))

    def tweetLikes(self, id):
        user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        url = "https://api.twitter.com/2/tweets/{}/liking_users?max_results=100".format(id)
        return url, user_fields

    def tweetRetweets(self, id):
        user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        url = "https://api.twitter.com/2/tweets/{}/retweeted_by?max_results=100".format(id)
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

        tweet_id = id

        try:
            if 'errors' in json_response:
                print(json_response['errors'])
                pass
            else:
                tweets_counter += json_response["meta"]["result_count"]
        except:
            pass

        if self.exitIfNotAuthorized(json_response):
            print("Tweet has been deleted: {}".format(id))
        else:
            self.insertUser(json_response)

            try:
                statusFile = open("analytics-status.csv", "r")
                status_content = eval(statusFile.read())
                if 'next_token' in status_content:
                    self.next_token = status_content['next_token']
                    if self.next_token:
                        json_response["meta"]["next_token"] = self.next_token
                else:
                    pass
            except FileNotFoundError:
                print('Status file does not exists.')

            statusFile = open("analytics-status.csv", "w")
            statusFile.write(str(json_response["meta"]))
            statusFile.close()

            while 'next_token' in json_response["meta"] and json_response["meta"]["next_token"]:

                sleep(2)

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

                statusFile = open("analytics-status.csv", "w+")
                statusFile.write(str(json_response["meta"]))
                statusFile.close()
                print("{} --> {}".format(str(datetime.now()), json_response['meta']['result_count']))
                self.insertUser(json_response)

            try:
                os.remove("analytics-status.csv")
            except:
                print('analytics-status.csv not found.')
                pass

            print("Total like counter:" + str(len(self.analytics)))

    def insertUser(self, json_response):
            print(json_response['data'])
            if 'data' in json_response:
                for i in json_response['data']:
                    self.analytics.append(
                        (
                            i['public_metrics']['followers_count'],
                            i['id'],
                            i['name'],
                            i['username'],
                            i['public_metrics']['following_count'],
                            i['public_metrics']['tweet_count'],
                            i['created_at'],
                            i['location'],
                            i['profile_image_url'],
                            i['description'],
                        )
                    )




