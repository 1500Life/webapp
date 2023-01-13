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
import convert_numbers

bearer_token=os.environ.get("BEARER_TOKEN_WEB")
redis_password=os.environ.get("REDIS_PASS")

class Command(BaseCommand):
    help = 'Full account check with mention'
    next_token = ''

    def handle(self, *args, **options):
        self.fire()
        self.stdout.write(self.style.SUCCESS('Account has been checked.'))

    def mentionRead(self):
        time = datetime.datetime.now() - datetime.timedelta(minutes=5)
        start_time = time.strftime('%Y-%m-%dT%H:%M:00.000Z')
        print(start_time)
        user_fields = "user.fields=id;tweet.fields=referenced_tweets,in_reply_to_user_id"
        url = "https://api.twitter.com/2/users/{}/mentions?start_time={}".format(os.environ.get("ADMIN_USER"), start_time)
        return url, user_fields

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2LikingUsersPython"
        return r

    def tweetRead(self, id):
        tweet_fields = "tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld"
        url = "https://api.twitter.com/2/tweets/{}".format(id)
        return url, tweet_fields

    def tweetLikes(self, id):
        user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        url = "https://api.twitter.com/2/tweets/{}/liking_users?max_results=100".format(id)
        return url, user_fields

    def connect_to_endpoint(self, url, user_fields, method):
        response = requests.request(method, url, auth=self.bearer_oauth, params=user_fields)
        return response.text

    def fire(self):
        website = 'https://1500.life/'
        chrome_extension = 'https://chrome.google.com/webstore/detail/yellowhattwitter/gheampocaolicfiiahnkhdclgdnoeoom'

        url, tweet_fields = self.mentionRead()
        
        json_response = json.loads(self.connect_to_endpoint(url, tweet_fields, 'GET'))

        if json_response['meta']['result_count']:
            for tweet in json_response['data']:

                user_id = tweet['in_reply_to_user_id']

                json_response = json.loads(self.connect_to_endpoint(url, tweet_fields, 'GET'))

                tweets = Tweets.objects.filter(author=user_id).values()

                user = Users.objects.filter(user_id=user_id)

                users_tweets = UsersTweets.objects.filter(users_id=user_id).values()

                labels = []
                tweets_fa = []
                for ut in users_tweets:
                    try:
                        tl = TweetsLabels.objects.filter(tweet_id=ut['tweets_id'])[0]
                        get_label = Labels.objects.filter(id=tl.label_id)[0]
                    except:
                        pass

                    labels.append(get_label.name)
                    tweets_fa.append(get_label.lang_fa)

                label_tweets = []

                for t in tweets:
                    try:
                        tl = TweetsLabels.objects.filter(tweet_id=t['id'])[0]
                        get_label = Labels.objects.filter(id=tl.label_id)[0]
                    except:
                        pass
                        
                    label_tweets.append(get_label.name)
                    tweets_fa.append(get_label.lang_fa)

                tweets_fa = list(dict.fromkeys(tweets_fa))

                if ((tweet['text'].find('@1500Life') != -1 or (tweet['text'].find('@1500life') != -1))):
                    if (tweet['text'].find('چک') != -1):
                        if 'referenced_tweets' in tweet:
                            redisClient = redis.Redis(password=redis_password)

                            if redisClient.get('full-check-{}'.format(tweet['id'])) == None:
                                label_list = []
                                label_counter = 0
                                label_list_result = ""
                                try:
                                    if len(labels) >= 1 or len(label_tweets) >= 1:
                                        if ('PS752' in labels) or ('PS752' in label_tweets):
                                            label_list.append('هواپیمای ۷۵۲ چک 💥✈️')
                                            label_counter += 1
                                        if ('ghasem' in labels) or ('ghasem' in label_tweets):
                                            label_list.append('قاسم‌چک 🍗')
                                            label_counter += 1
                                        if ('niac' in labels) or ('niac' in label_tweets):
                                            label_list.append('نایاک چک 💰')
                                            label_counter += 1
                                        if ('arvan_cloud' in labels) or ('arvan_cloud' in label_tweets):
                                            label_list.append('ابرآروان چک')
                                            label_counter += 1
                                        if ('famtrip' in labels) or ('famtrip' in label_tweets):
                                            label_list.append('فم‌تریپ چک')
                                            label_counter += 1
                                        if ('mullah_team' in labels) or ('mullah_team' in label_tweets):
                                            label_list.append('تیم ملا چک 🩸⚽')
                                            label_counter += 1
                                        
                                        page_link = 'https://1500.life/show?username={}'.format(user[0].user_name)

                                        for item in label_list:
                                            label_list_result += "- {}\n".format(item)
                                        
                                        message = "شناسه کاربر:  {}\n{} فعالیت مشکوک از {} در پایگاه داده ما یافت شد. \n\n{}\n  اطلاعات کامل در سایت. \n{}\n\n ⚠️ نتایج بات 🤖".format(user[0].user_id, convert_numbers.english_to_persian(len(labels)+len(label_tweets)), user[0].user_name, label_list_result, page_link)

                                        self.sendReply(message, tweet['id'])
                                    else:
                                        message = "❌ بی‌نتیجه ❌\nفعالیتی از این کاربر در پایگاه داده ما یافت نشد، توجه داشته باشید این به معنای پاک بود سابقه کاربر نیست، برای جستجوی راحت‌تر می‌توانید از افزونه کروم ما بهتره ببرید \n{}\n یا به سایت ما رجوع کنید ‌\n{}".format(chrome_extension, website)
                                        self.sendReply(message, tweet['id'])
                                except Exception as e:
                                    print(e)
                                    message = "❌ بی‌نتیجه ❌\nفعالیتی از این کاربر در پایگاه داده ما یافت نشد، توجه داشته باشید این به معنای پاک بود سابقه کاربر نیست، برای جستجوی راحت‌تر می‌توانید از افزونه کروم ما بهتره ببرید \n{}\n یا به سایت ما رجوع کنید ‌\n{}".format(chrome_extension, website)
                                    self.sendReply(message, tweet['id'])
                                print(message)
                                redisClient.set('full-check-{}'.format(tweet['id']), 0)
                            else:
                                print('The queue is empty!')

                    if (tweet['text'].find('توییت راهنما') != -1):
                        redisClient = redis.Redis(password=redis_password)

                        if redisClient.get('help-{}'.format(tweet['id'])) == None:
                            message = "سلام! 🤖\nمن کمکتون می‌کنم فعالیت‌های ناامن توییتر رو شناسایی کنید.\n\nبرای کار با من کافیه زیر یکی از توییت‌هایی که می‌خواید صاحب اکانتش چک بشه اسم اکانت ما رو منشن کنید و بعد کلمه «چک» رو بنویسید، در کمتر از ۱ دقیقه ⏱️ نتیجه برای شما ارسال میشه مثال 👇\n https://twitter.com/1500Life/status/1588469620960215041"
                            self.sendReply(message, tweet['id'])
                            print(message)
                            redisClient.set('help-{}'.format(tweet['id']), 0)

                    if (tweet['text'].find('گزارش توییت') != -1):

                        redisClient = redis.Redis(password=redis_password)

                        if redisClient.get('report-tweet-{}-{}-{}'.format(user_id, tweet['id'], tweet['referenced_tweets'][0]['id'])) == None:

                            print('Internet Archive')
                            internet_archive_result = ''
                            url = 'https://twitter.com/twitter/status/' + tweet['referenced_tweets'][0]['id']
                            user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
                            save_api = WaybackMachineSaveAPI(url, user_agent)
                            try:
                                internet_archive_result = save_api.save()
                            except:
                                print('error during archiving')
                                pass
                            
                            user_report_file = open("user_report.txt", "a+")
                            line = ["user:{} - tweet:{} - archive:{}\n".format(user_id, tweet['referenced_tweets'][0]['id'], internet_archive_result)]
                            user_report_file.writelines(line)
                            user_report_file.close()

                            message = "گزارش 📝 شما با موفقیت برای بررسی ثبت شد \n\n شناسه کاربر: {} \n\n شناسه توییت: {} \n\n آرشیو توییت: {} \n\n نتایج بات 🤖".format(user_id, tweet['referenced_tweets'][0]['id'], internet_archive_result)
                            self.sendReply(message, tweet['id'])
                            print(message)
                            redisClient.set('report-tweet-{}-{}-{}'.format(user_id, tweet['id'], tweet['referenced_tweets'][0]['id']), 0)

                    if (tweet['text'].find('آنالیز توییت') != -1):
                        redisClient = redis.Redis(password=redis_password)
                        tweets_counter = 0

                        if 'referenced_tweets' in tweet:
                            if tweet['referenced_tweets'][0]['type'] == 'replied_to':
                                id = tweet['referenced_tweets'][0]['id']
                            else:
                                message = "به نظر می‌رسد که به روش درستی از «آنالیز توییت» استفاده نکرده‌اید، شما باید در جواب یک توییت این درخواست را بکنید."
                                self.sendReply(message, tweet['id'])
                        else:
                            message = "به نظر می‌رسد در حال حاضر مشکل فنی داریم، لطفا بعدا امتحان کنید"
                            self.sendReply(message, tweet['id'])
                    
                        url, tweet_fields = self.tweetLikes(id)
                        likes_json_response = json.loads(self.connect_to_endpoint(url, tweet_fields, 'GET'))

                        count = 0
                        user_exist = 0
                        user_not_exist = 0
                        default_profile = 0
                        followers_count = 0
                        health_index = 0
                     
                        if (int(likes_json_response['meta']['result_count']) > 0):
                            for item in likes_json_response['data']:
                                user = Users.objects.filter(user_id=likes_json_response['data'][count]['id']).values()

                                if(item['profile_image_url'] == 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png'):
                                    default_profile += 1

                                if item['public_metrics']['followers_count'] >= 1000:
                                    followers_count += 1
                                if(user):
                                    user_exist += 1
                                else:
                                    user_not_exist += 1
                                count += 1
                            
                            analyse_result = round(user_exist/(user_exist+user_not_exist)*100)

                            health_index = round((100-analyse_result)/10)

                            if redisClient.get('analyse-tweet-{}'.format(tweet['id'])) == None:
                                message = "آنالیز این توییت براساس ۱۰۰ لایک آخر\n\n  -  رتبه توییت {} از ۱۰ است \n  -  حدود {} درصد از لایک‌ کننده‌ها دارای فعالیت ناامن هستند. 🧌\n  -  تعداد {} کاربر روح لایک کرده‌اند 👻\n  -  تعداد {} نفر از لایک کننده‌ها دارای حداقل ۱۰۰۰ فالاور هستند 🏃\n\n ⚠️ نتایج بات 🤖".format(convert_numbers.english_to_persian(health_index), convert_numbers.english_to_persian(analyse_result), convert_numbers.english_to_persian(default_profile), convert_numbers.english_to_persian(followers_count))
                                self.sendReply(message, tweet['id'])
                                print(message)
                                redisClient.set('analyse-tweet-{}'.format(tweet['id']), 0)
                        else:
                            print('no result')


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

    