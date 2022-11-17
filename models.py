from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=200)
    user_name = models.CharField(max_length=200)
    created_at = models.DateField(null=True)
    description = models.CharField(max_length=200,null=True)
    name = models.CharField(max_length=200,null=True)
    profile_image_url = models.CharField(max_length=200,null=True)
    protected = models.BooleanField(null=True)
    public_metrics = models.CharField(max_length=200,null=True)
    url = models.CharField(max_length=200,null=True)
    verified = models.BooleanField(null=True)
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['user_name', 'user_id'], name='unique_migration_User_combination'
                )
        ]

class UserTweetLikes(models.Model):
    id = models.AutoField(primary_key=True)
    author_id = models.CharField(max_length=200)
    tweet_id = models.CharField(max_length=200)
    liker_id = models.CharField(max_length=200)
    user_name = models.CharField(max_length=200)
    created_at = models.DateField(null=True)
    description = models.CharField(max_length=200,null=True)
    name = models.CharField(max_length=200,null=True)
    profile_image_url = models.CharField(max_length=200,null=True)
    protected = models.BooleanField(null=True)
    verified = models.BooleanField(null=True)
    followers = models.CharField(max_length=200,null=True)
    following = models.CharField(max_length=200,null=True)


class UsersTweets(models.Model):
    tweets_id = models.CharField(max_length=200)
    users_id = models.CharField(max_length=200)
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['tweets_id', 'users_id'], name='unique_migration_UserTweets_combination'
                )
        ]

class Tweets(models.Model):
    id = models.CharField(max_length=200,primary_key=True)
    author = models.CharField(max_length=200,null=True)
    archive = models.CharField(max_length=500,null=True)
    conversation_id = models.CharField(max_length=200,null=True)
    created_at = models.CharField(max_length=200,null=True)
    in_reply_to_user_id = models.CharField(max_length=200,null=True)
    lang = models.CharField(max_length=200,null=True)
    public_metrics = models.CharField(max_length=1000,null=True)
    possibly_sensitive = models.CharField(max_length=200,null=True)
    referenced_tweets = models.CharField(max_length=200,null=True)
    reply_settings = models.CharField(max_length=2000,null=True)
    source = models.CharField(max_length=1000,null=True)
    text = models.CharField(max_length=1000,null=True)
    retweet_count = models.CharField(max_length=20,null=True)
    reply_count = models.CharField(max_length=20,null=True)
    quote_count = models.CharField(max_length=20,null=True)
    like_count = models.CharField(max_length=20,null=True)
    deleted = models.BooleanField(null=True)

class TweetsLabels(models.Model):
    tweet_id = models.CharField(max_length=200)
    label_id = models.CharField(max_length=200)
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['tweet_id', 'label_id'], name='unique_migration_Tweetslabels_combination'
                )
        ]

class Labels(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    lang_fa = models.CharField(max_length=400,null=True)
    lang_en = models.CharField(max_length=400,null=True)
    hatag = models.CharField(max_length=200,null=True)
    priority = models.CharField(max_length=200,null=True)
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['name'], name='unique_migration_labels_combination'
                )
        ]