# Webservice
This document covering the 1500Life Web and console services in order to make our process more clear for our users. Our webservice powered by [Django framework](https://www.djangoproject.com/). 

## Prequisites
* Python3
* Pip3
* Django
* Postgres or any other DBMS.
* Redis

## Serve the food
Please follow installation process on Ubuntu on [this page](https://www.digitalocean.com/community/tutorials/how-to-install-django-and-set-up-a-development-environment-on-ubuntu-20-04).

### Servie configuration on init.d

```
[Unit]
Description=Gunicorn daemon for Django Project
Before=nginx.service
After=network.target

[Service]
WorkingDirectory=[PATH_TO_YOUR_APP]
ExecStart=/usr/bin/gunicorn3 --name=[YOUR_PROJECT_NAME] --pythonpath=[PATH_TO_YOUR_APP] --bind unix:[PATH_TO_SOCKET]/gunicorn.socket --config /etc/gunicorn.d/gunicorn.py django_project.wsgi:application
Restart=always
SyslogIdentifier=gunicorn
User=[django_user]
Group=[django_user]


[Install]
WantedBy=multi-user.target
```

Then Start the service
```
service gunicorn start
```

And let's create a file for bulk insert list, there is two opptions for nightly runs and adding new Tweets to the list.

```
{   "labels": [
    {"name": "ghasem", "priority": 1, "lang_fa": "قاسم چک مثبت" },
],
"tweet_backup": [
    {"tweet_id": "1591485049756876801", "label_name": "ghasem"},
],
 "tweets": [
    {"tweet_id": "1591485049756876801", "label_name": "1591485049756876801"},
 ]  
}
```
By calling console full_check with 1 0 paramter you with be able to add the new Tweets for "tweets" section.

```
python3 manage.py start_check 1 0
```

And by turning the second switch on you will be able to run the nightly runs as well.

```
python3 manage.py start_check 1 1
```

### Environment variables
You can define the variables in your profile file or even ```/etc/environments```.

| Env | Description |
|-----|-------------|
|CONSUMER_KEY_WEB|Twitter Consumer key for webservice|
|CONSUMER_SECRET_WEB|Twitter Consumer secret for webservice| 
|BEARER_TOKEN_WEB|Twitter brear token for webservice|
|CONSUMER_KEY_CONSOLE|Twitter Consumer key for console|
|CONSUMER_SECRET_CONSOLE|Twitter Consumer secret for console|
|BEARER_TOKEN_CONSOLE|Twitter Brear token for console commands|
|REDIS_PASS|Redis password|
|CONSUMER_KEY_WEB|Twitter Consumer key for websevice|
|CONSUMER_SECRET_WEB|Twitter Consumer secret for webservice|
|ACCESS_TOKEN_WEB|Twitter Access token for webservice|
|ACCESS_TOKEN_SECRET_WEB|Twitter token secret for webservice|
|ADMIN_USER|Twitter API admin user ID|
