# Generated by Django 4.0.4 on 2022-07-19 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0007_userstocktransactions_alter_company_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashstatements',
            name='company',
        ),
        migrations.RemoveField(
            model_name='incomestatement',
            name='company',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='BalanceStatement',
        ),
        migrations.DeleteModel(
            name='CashStatements',
        ),
        migrations.DeleteModel(
            name='IncomeStatement',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]