# Generated by Django 5.1.7 on 2025-03-17 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfid_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidat',
            name='photo_profile',
            field=models.ImageField(default='photos de profile/candidat_img.jpg', upload_to='photos de profile'),
        ),
    ]
