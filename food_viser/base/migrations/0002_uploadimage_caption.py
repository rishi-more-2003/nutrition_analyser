# Generated by Django 4.0.4 on 2022-11-16 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadimage',
            name='caption',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
