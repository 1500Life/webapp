from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
import requests
import os
import json
from polls.models import *
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.text import Truncator
from django.views.generic.list import ListView

bearer_token = os.environ.get("BEARER_TOKEN_WEB")

def index(request):
    context = {}
    context['users'] = Users.objects.count()
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

def under(request):
    context = {}
    template = loader.get_template('under-struct.html')
    return HttpResponse(template.render(context, request))

def privacy_policy(request):
    context = {}
    template = loader.get_template('privacy_policy.html')
    return HttpResponse(template.render(context, request))

def archive(request):
    context = {}
    template = loader.get_template('archive.html')
    return HttpResponse(template.render(context, request))

def label(request):
    context = {}
    context['label'] = Tweets.objects.all().order_by('like_count').values()
    # paginator = Paginator(context['label'], 10)

    template = loader.get_template('label.html')
    return HttpResponse(template.render(context, request))

def tweets(request):
    context = {}
    context['tweets'] = Tweets.objects.all().order_by('id').values()
    # paginator = Paginator(context['tweets'], 10)

    template = loader.get_template('tweets.html')
    return HttpResponse(template.render(context, request))

def api_user(request):
    context = {}
    tweets = []

    if 'username' in request.GET:
        username = request.GET['username']
        username = username.replace('@', '')
        username = username.replace('https://twitter.com/', '')
        user = Users.objects.filter(user_name__iexact=username)

        try:
            if user:
                user = user[0]
                tweets = Tweets.objects.filter(author=user.user_id).values()
            else:
                url, user_fields = readUser(username)
                json_response = json.loads(connect_to_endpoint(url, user_fields, 'GET'))

                if 'id' in json_response['data']:
                    user = Users.objects.filter(user_id=json_response['data']['id'])

                    if user:
                        user = user[0]
                        tweets = Tweets.objects.filter(author=user.user_id).values()

                        Users.objects.create(
                            user_name = json_response['data']['username'],
                            user_id = json_response['data']['id'],
                            created_at = parse_date(json_response['data']['created_at']),
                            description = Truncator(json_response['data']['description']).chars(200),
                            name = json_response['data']['name'],
                            profile_image_url = json_response['data']['profile_image_url'],
                            protected = json_response['data']['protected'],
                            public_metrics = json_response['data']['public_metrics'],
                            verified = json_response['data']['verified'],
                        ).save()
                    else:
                        response = JsonResponse({'error': 'not-found'})
                        response["Access-Control-Allow-Origin"] = "*"
                        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                        response["Access-Control-Max-Age"] = "1000"
                        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
                        return response
                else:
                    response = JsonResponse({'error': 'not-found'})
                    response["Access-Control-Allow-Origin"] = "*"
                    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                    response["Access-Control-Max-Age"] = "1000"
                    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
                    return response
        except:
            response = JsonResponse({'error': 'not-found'})
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Max-Age"] = "1000"
            response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
            return response
        users_tweets = UsersTweets.objects.filter(users_id=user.user_id).values()

        accounts = Users.objects.filter(user_id=user.user_id).values()

        labels = []
        for ut in users_tweets:
            try:
                tl = TweetsLabels.objects.filter(tweet_id=ut['tweets_id'])[0]
                get_label = Labels.objects.filter(id=tl.label_id)[0]
                tweet = Tweets.objects.filter(id=ut['tweets_id'])[:1].get()
                labels.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': get_label.name,
                    'fa': get_label.lang_fa,
                    'archive' : tweet.archive,
                    })
            except:
                pass

        label_tweets = []
        try:
            for tweet in tweets:
                tl = TweetsLabels.objects.filter(tweet_id=tweet['id'])[0]
                get_label = Labels.objects.filter(id=tl.label_id)[0]
                label_tweets.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': get_label.name,
                    'fa': get_label.lang_fa,
                    'archive' : tweet['archive']
                    })
        except:
            pass

        
        context['user'] = user
        context['labels'] = labels
        context['tweets'] = label_tweets
        context['accounts'] = accounts

        response = JsonResponse({'label_tweets': label_tweets, 'labels': labels, 'accounts': list(accounts)})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response

def user_test(request):
    context = {}
    tweets = []

    if 'username' in request.GET:
        username = request.GET['username']
        username = username.replace('@', '')
        username = username.replace('https://twitter.com/', '')
        user = Users.objects.filter(user_name__iexact=username)

        try:
            if user:
                user = user[0]
                tweets = Tweets.objects.filter(author=user.user_id).values()
            else:
                url, user_fields = readUser(username)
                json_response = json.loads(connect_to_endpoint(url, user_fields, 'GET'))

                if 'id' in json_response['data']:
                    user = Users.objects.filter(user_id=json_response['data']['id'])

                    if user:
                        user = user[0]
                        tweets = Tweets.objects.filter(author=user.user_id).values()
                        Users.objects.create(
                            user_name = json_response['data']['username'],
                            user_id = json_response['data']['id'],
                            created_at = parse_date(json_response['data']['created_at']),
                            description = Truncator(json_response['data']['description']).chars(200),
                            name = json_response['data']['name'],
                            profile_image_url = json_response['data']['profile_image_url'],
                            protected = json_response['data']['protected'],
                            public_metrics = json_response['data']['public_metrics'],
                            verified = json_response['data']['verified'],
                        ).save()
                    else:
                        messages.error(request, 'سابقه‌ای از این کاربر در پایگاه داده ما یافت نشد')
                        template = loader.get_template('user_test.html')
                        return HttpResponse(template.render(context, request))
                else:
                    messages.error(request, 'سابقه‌ای از این کاربر در پایگاه داده ما یافت نشد')
                    template = loader.get_template('user_test.html')
                    return HttpResponse(template.render(context, request))
        except:
            messages.error(request, 'سابقه‌ای از این کاربر در پایگاه داده ما یافت نشد')
            template = loader.get_template('user_test.html')
            return HttpResponse(template.render(context, request))

        users_tweets = UsersTweets.objects.filter(users_id=user.user_id).values()

        accounts = Users.objects.filter(user_id=user.user_id).values()

        labels = []
        for ut in users_tweets:
            try:
                tl = TweetsLabels.objects.filter(tweet_id=ut['tweets_id'])[0]
            except:
                pass
            try:
                get_label = Labels.objects.filter(id=tl.label_id)[0]
                tweet = Tweets.objects.filter(id=ut['tweets_id'])[:1].get()
                labels.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': get_label.name,
                    'fa': get_label.lang_fa,
                    'archive' : tweet.archive,
                    'text': tweet.text,
                    'like_count': tweet.like_count,
                })
            except:
                tweet = Tweets.objects.filter(id=ut['tweets_id'])[:1].get()
                labels.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': 'no_label',
                    'fa': 'فاقد برچسب',
                    'archive' : tweet.archive,
                    'text': tweet.text,
                    'like_count': tweet.like_count,
                })



        label_tweets = []

        try:
            for tweet in tweets:
                tl = TweetsLabels.objects.filter(tweet_id=tweet['id'])[0]
                get_label = Labels.objects.filter(id=tl.label_id)[0]
                get_tweet = Tweets.objects.filter(id=tl.tweet_id)[:1].get()
                label_tweets.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': get_label.name,
                    'fa': get_label.lang_fa,
                    'archive' : tweet['archive'],
                    'text': get_tweet.text,
                    'like_count': get_tweet.like_count,
                    })
        except:
            pass

        context['user'] = user
        context['labels'] = labels
        context['tweets'] = label_tweets
        context['accounts'] = accounts
        template = loader.get_template('user_test.html')
        return HttpResponse(template.render(context, request))

def show(request):
    context = {}
    tweets = []

    if 'username' in request.GET:
        username = request.GET['username']
        username = username.replace('@', '')
        username = username.replace('https://twitter.com/', '')
        user = Users.objects.filter(user_name__iexact=username)

        try:
            if user:
                user = user[0]
                tweets = Tweets.objects.filter(author=user.user_id).values()
            else:
                url, user_fields = readUser(username)
                json_response = json.loads(connect_to_endpoint(url, user_fields, 'GET'))

                if 'id' in json_response['data']:
                    user = Users.objects.filter(user_id=json_response['data']['id'])

                    if user:
                        user = user[0]
                        tweets = Tweets.objects.filter(author=user.user_id).values()
                        Users.objects.create(
                            user_name = json_response['data']['username'],
                            user_id = json_response['data']['id'],
                            created_at = parse_date(json_response['data']['created_at']),
                            description = Truncator(json_response['data']['description']).chars(200),
                            name = json_response['data']['name'],
                            profile_image_url = json_response['data']['profile_image_url'],
                            protected = json_response['data']['protected'],
                            public_metrics = json_response['data']['public_metrics'],
                            verified = json_response['data']['verified'],
                        ).save()
                    else:
                        messages.error(request, 'سابقه‌ای از این کاربر در پایگاه داده ما یافت نشد')
                        template = loader.get_template('user.html')
                        return HttpResponse(template.render(context, request))
                else:
                    messages.error(request, 'سابقه‌ای از این کاربر در پایگاه داده ما یافت نشد')
                    template = loader.get_template('user.html')
                    return HttpResponse(template.render(context, request))
        except:
            messages.error(request, 'سابقه‌ای از این کاربر در پایگاه داده ما یافت نشد')
            template = loader.get_template('user.html')
            return HttpResponse(template.render(context, request))

        users_tweets = UsersTweets.objects.filter(users_id=user.user_id).values()

        accounts = Users.objects.filter(user_id=user.user_id).values()

        labels = []
        for ut in users_tweets:
            try:
                tl = TweetsLabels.objects.filter(tweet_id=ut['tweets_id'])[0]
            except:
                pass
            try:
                get_label = Labels.objects.filter(id=tl.label_id)[0]
                tweet = Tweets.objects.filter(id=ut['tweets_id'])[:1].get()
                labels.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': get_label.name,
                    'fa': get_label.lang_fa,
                    'archive' : tweet.archive,
                    'text': tweet.text,
                    'like_count': tweet.like_count,
                })
            except:
                tweet = Tweets.objects.filter(id=ut['tweets_id'])[:1].get()
                labels.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': 'no_label',
                    'fa': 'فاقد برچسب',
                    'archive' : tweet.archive,
                    'text': tweet.text,
                    'like_count': tweet.like_count,
                })



        label_tweets = []

        try:
            for tweet in tweets:
                tl = TweetsLabels.objects.filter(tweet_id=tweet['id'])[0]
                get_label = Labels.objects.filter(id=tl.label_id)[0]
                get_tweet = Tweets.objects.filter(id=tl.tweet_id)[:1].get()
                label_tweets.append({
                    'label_id': tl.label_id,
                    'tweet_id': tl.tweet_id,
                    'name': get_label.name,
                    'fa': get_label.lang_fa,
                    'archive' : tweet['archive'],
                    'text': get_tweet.text,
                    'like_count': get_tweet.like_count,
                    })
        except:
            pass

        context['user'] = user
        context['labels'] = labels
        context['tweets'] = label_tweets
        context['accounts'] = accounts
        template = loader.get_template('user.html')
        return HttpResponse(template.render(context, request))

def bearer_oauth(r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2LikingUsersPython"
        return r

def readUser(user_name):
    user_fields = "user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
    url = "https://api.twitter.com/2/users/by/username/{}".format(user_name)
    return url, user_fields

def connect_to_endpoint(url, user_fields, method):
    response = requests.request(method, url, auth=bearer_oauth, params=user_fields)
    return response.text