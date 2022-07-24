# Generated by Django 4.0.4 on 2022-05-24 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_userfollowedcompanies_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='currency',
            field=models.CharField(choices=[('PLN', 'PLN'), ('EUR', 'EUR'), ('USD', 'USD')], default='PLN', max_length=10),
        ),
    ]