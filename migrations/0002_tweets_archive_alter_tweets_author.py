# Generated by Django 4.0.6 on 2022-07-31 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweets',
            name='archive',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tweets',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
