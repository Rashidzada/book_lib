# Generated by Django 5.0.4 on 2024-05-07 12:20

import embed_video.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_book_youtube_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='youtube_link',
            field=embed_video.fields.EmbedVideoField(blank=True, null=True),
        ),
    ]
