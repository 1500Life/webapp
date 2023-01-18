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
from django.db.models import Count

bearer_token = os.environ.get("BEARER_TOKEN_CONSOLE")

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    label_name = ''
    next_token = ''
    tweet_archive = ''
    tweet_details = []

    def handle(self, *args, **options):
        count = Users.objects.all().count()
        steper = 100

        for i in range(0, count, steper):
            self.user_get = Users.objects.all().order_by('id')[i:steper+i] 
            self.fire(i, steper+i)
            print('-->', i)
        self.stdout.write(self.style.SUCCESS('Successfully closed Users'))

    def userRead(self, id):
        user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        url = "https://api.twitter.com/1.1/users/lookup.json?user_id={}".format(id)
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

    def connect_to_endpoint(self, url, user_fields, start, end):
        response = requests.request("GET", url, auth=self.bearer_oauth, params=user_fields)
        if response:
            if response.status_code != 200:
                print('Too many requests, wait 15 minutes')
                sleep(900)
                return False
            else:
                return response.json()
        else:
            print(response.json())
            print('Too many requests - wait 15 minutes')
            sleep(900)
            return False

    def fire(self, start, end):
        all_users = ''

        for user in self.user_get.values():
            if all_users != '':
                all_users = all_users + ',' + user['user_id']
            else:
                all_users = user['user_id']

        url, user_fields = self.userRead(all_users)
        json_response = self.connect_to_endpoint(url, user_fields, start, end)

        if json_response == False:
            url, user_fields = self.userRead(all_users)
            json_response = self.connect_to_endpoint(url, user_fields, start, end)  
        
        try:
            for user in json_response:
                UsersInfo.objects.create(
                        user_id = user['id'],
                        name = user['name'],
                        screen_name = user['screen_name'],
                        location = user['location'],
                        description = user['description'],
                        protected = user['protected'],
                        followers_count = user['followers_count'],
                        friends_count = user['friends_count'],
                        listed_count = user['listed_count'],
                        created_at = user['created_at'],
                        favourites_count = user['favourites_count'],
                        utc_offset = user['utc_offset'],
                        time_zone = user['time_zone'],
                        geo_enabled = user['geo_enabled'],
                        verified = user['verified'],
                        statuses_count = user['statuses_count'],
                        lang = user['lang'],
                        contributors_enabled = user['contributors_enabled'],
                        profile_image_url = user['profile_image_url']
                    ).save()
        except:
            print(json_response)
            pass
        print(end)

