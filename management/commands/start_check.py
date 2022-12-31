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
    tweet_archive = ''
    tweet_details = []

    def add_arguments(self, parser):
        parser.add_argument('tweet_id', nargs='+', type=int)
        parser.add_argument('backup', nargs='+', type=int)

    def handle(self, *args, **options):
        tweet_target = 'tweets'

        if 'backup' in options:
            if options['backup'][0] == 1:
                tweet_target = 'tweet_backup'


        statusFile = open("bulk_insert.json", "r")
        bulk_insert = eval(statusFile.read())

        for label in bulk_insert['labels']:
            label_query = Labels.objects.filter(name=label['name'])
            if len(label_query) == 0:
                Labels.objects.create(
                    name = label['name'],
                    priority = label['priority'],
                    lang_fa = label['lang_fa'],
                ).save()
                print('Label "%s" has been inserted.' % label['name'])

        for tweet in bulk_insert[tweet_target]:
            self.label_name = tweet['label_name']
            self.fire(tweet['tweet_id'])
            try:
                self.tweet_archive = Tweets.objects.filter(id=tweet['tweet_id'])[:1].get()
                self.tweet_archive = self.tweet_archive
            except Exception as e:
                self.tweet_archive = None
            self.archive(tweet['tweet_id'])

        self.stdout.write(self.style.SUCCESS('Successfully closed Tweet'))
    
    def is_archive(self, url):
        archive_org = 'https://archive.org/wayback/available?url='
        response = requests.request("GET", archive_org + url)
        response = response.json()

        if 'closest' in response['archived_snapshots']:
            return True
        else:
            return False

    def archive(self, tweet_id):
        try:
            tweet = self.tweet_archive

            if (tweet.archive == None):
                print('Start archiving tweet {}'.format(tweet))
                internet_archive_result = ''
                url = 'https://twitter.com/twitter/status/' + tweet_id
                user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
                
                internet_archive_save_url = 'http://web.archive.org/save/twitter.com/twitter/status/' + tweet_id
                internet_archive_url = internet_archive_save_url.replace("save", "web")
                if self.is_archive(url):
                    print('Archive exists just update request...')
                    tweet.archive = internet_archive_url
                    tweet.save()
                else:
                    save_api = WaybackMachineSaveAPI(url, user_agent)
                    try:
                        print('Save api request...')
                        tweet.archive = internet_archive_url
                        tweet.save()
                        internet_archive_result = save_api.save()
                        print('Request from Internet Archive response saved!')
                        print('Tweet: ' +  tweet_id + ' - updated (archive) with ' + internet_archive_result )
                    except Exception as e:
                        print(e)
                print('Internet Archive status: ' + str(internet_archive_result))
        except Exception as e:
            print('Tweet not exist in DB for archive.')

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
            try:
                get_tweet = Tweets.objects.filter(id=tweet_id)[:1].get()
                get_tweet.deleted = True
                get_tweet.save()
            except:
                print("Tweet has been deleted and has not archived: {}".format(id))
            print("Tweet has been deleted: {}".format(id))
        else:
            self.insertTweet(id, self.label_name)
            self.insertUser(json_response, tweets_counter, tweet_id)
            self.insertTweetDetails(tweet_id)

            try:
                statusFile = open("status.csv", "r")
                status_content = eval(statusFile.read())
                if 'next_token' in status_content:
                    self.next_token = status_content['next_token']
                    if self.next_token:
                        json_response["meta"]["next_token"] = self.next_token
                else:
                    pass
            except FileNotFoundError:
                print('Status file does not exists.')

            statusFile = open("status.csv", "w")
            statusFile.write(str(json_response["meta"]))
            statusFile.close()

            self.insertTweet(tweet_id, self.label_name)

            while 'next_token' in json_response["meta"] and json_response["meta"]["next_token"]:

                tweets_counter += json_response["meta"]["result_count"]

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

                statusFile = open("status.csv", "w")
                statusFile.write(str(json_response["meta"]))
                statusFile.close()
                print("{} --> {}".format(str(datetime.now()), json_response['meta']['result_count']))
                self.insertUser(json_response, tweets_counter, tweet_id)

            self.insertTweetDetails(tweet_id)
            try:
                os.remove("status.csv")
            except:
                print('status.csv not found.')
                pass

            print("Total like counter:" + str(tweets_counter))

    def insertUser(self, json_response, tweets_counter, tweet_id):
            user_bulk_list = list()

            if 'data' in json_response:
                for i in json_response['data']:
                    if i['username']:
                        user_bulk_list.append(
                            Users(
                                user_name = i['username'],
                                user_id = i['id'],
                                created_at = parse_date(i['created_at']),
                                description = Truncator(i['description']).chars(200),
                                name = i['name'],
                                profile_image_url = i['profile_image_url'],
                                protected = i['protected'],
                                public_metrics = i['public_metrics'],
                                verified = i['verified'],
                            )
                        )

                Users.objects.bulk_create(user_bulk_list, ignore_conflicts=True)

                for i in json_response['data']:
                    try:
                        UsersTweets.objects.create(
                            users_id = i['id'],
                            tweets_id = tweet_id,
                        ).save()
                        print("%s - \tUser %s[%s] \t\t\t %s tweet" %(str(datetime.now()),i['username'],i['id'], tweet_id))
                    except:
                        pass

                tweets_counter += json_response["meta"]["result_count"]
            else:
                pass

    def insertTweetDetails(self, tweet_id):
        tweet = Tweets.objects.filter(id=tweet_id)

        if len(tweet) > 0:

            print(tweet[0].author, tweet[0].archive)
            url, tweet_fields = self.tweetRead(tweet_id)
            json_response = self.connect_to_endpoint(url, tweet_fields, tweet_id)
            author_id = json_response['data']['author_id']
            
            print('-------->')
            print(json_response['data']['public_metrics']['retweet_count'])
            if json_response['data']['text']:
                in_reply_to_user_id = 0
                if ('in_reply_to_user_id' in json_response['data']):
                    in_reply_to_user_id = json_response['data']['in_reply_to_user_id'] 
                
                referenced_tweets = ''

                print(json_response['data'])
                if ('referenced_tweets' in json_response['data']):
                    referenced_tweets = json_response['data']['referenced_tweets'] 

                tweet_author = Tweets.objects.filter(id=tweet_id)[:1].get()
                if tweet_author.author == None:
                    tweet_author.author = author_id
                    tweet_author.text = json_response['data']['text']
                    tweet_author.created_at = json_response['data']['created_at']
                    tweet_author.conversation_id = json_response['data']['conversation_id']
                    tweet_author.in_reply_to_user_id = in_reply_to_user_id
                    tweet_author.lang = json_response['data']['lang']
                    tweet_author.public_metrics = json_response['data']['public_metrics']
                    tweet_author.possibly_sensitive = json_response['data']['possibly_sensitive']
                    tweet_author.referenced_tweets = referenced_tweets
                    tweet_author.reply_settings = json_response['data']['reply_settings']
                    tweet_author.retweet_count = json_response['data']['public_metrics']['retweet_count']
                    tweet_author.reply_count = json_response['data']['public_metrics']['reply_count']
                    tweet_author.like_count = json_response['data']['public_metrics']['like_count']
                    tweet_author.quote_count = json_response['data']['public_metrics']['quote_count']
                    tweet_author.save()
                print(str(datetime.now()) + ' - Tweet: ' +  tweet_id + ' - updated (author) with ' + author_id + json_response['data']['text'] )

                url, tweet_fields = self.userRead(author_id)
                json_response = self.connect_to_endpoint(url, tweet_fields, tweet_id)
                user = json_response['data']

                userQuery = Users.objects.filter(user_id=author_id)
                if len(userQuery) <= 0:
                    Users(
                            user_name = user['username'],
                            user_id = user['id'],
                            created_at = parse_date(user['created_at']),
                            description = Truncator(user['description']).chars(200),
                            name = user['name'],
                            profile_image_url = user['profile_image_url'],
                            protected = user['protected'],
                            public_metrics = user['public_metrics'],
                            verified = user['verified'],
                        ).save()
                    print(str(datetime.now()) + ' - New user has been added to users list for author: ' +  user['id'])

    def insertTweet(self, tweet_id, label_name):

        tweet = Tweets.objects.filter(id=tweet_id)
        if len(tweet) <= 0:
            Tweets(id = tweet_id).save()
        
        try:
            label = Labels.objects.filter(name=label_name)
            print(len(label))
            if len(label) > 0:
                label = label[0]
                tweetslabesl = TweetsLabels.objects.create(
                    label_id = label.id,
                    tweet_id = tweet_id,
                ).save()
            else:
                print(str(datetime.now()) + ' - Create new Label.')
                label = Labels.objects.create(name=label_name).save()
                LastInsertId = (Labels.objects.last()).id

                print(str(datetime.now()) + ' - Connect tweet to label')
                tweetslabesl = TweetsLabels.objects.create(
                    label_id = LastInsertId,
                    tweet_id = tweet_id,
                ).save()             
        except:
            pass

