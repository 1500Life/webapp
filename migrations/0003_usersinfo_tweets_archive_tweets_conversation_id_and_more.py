# Generated by Django 4.1.1 on 2023-01-14 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_tweetreports_tweets_archive_tweets_conversation_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestap', models.DateTimeField(auto_now_add=True)),
                ('user_id', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('screen_name', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('protected', models.CharField(max_length=200)),
                ('followers_count', models.CharField(max_length=200)),
                ('friends_count', models.CharField(max_length=200)),
                ('listed_count', models.CharField(max_length=200)),
                ('created_at', models.CharField(max_length=200)),
                ('favourites_count', models.CharField(max_length=200)),
                ('utc_offset', models.CharField(max_length=200)),
                ('time_zone', models.CharField(max_length=200)),
                ('geo_enabled', models.CharField(max_length=200)),
                ('verified', models.CharField(max_length=200)),
                ('statuses_count', models.CharField(max_length=200)),
                ('lang', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('contributors_enabled', models.CharField(max_length=200)),
                ('profile_image_url', models.CharField(max_length=200)),
            ],
        ),
    ]
