# Generated by Django 5.1.4 on 2024-12-16 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_post_publish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(max_length=250, unique_for_date='publish'),
        ),
    ]
