# Generated by Django 4.0.4 on 2022-07-22 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0008_remove_cashstatements_company_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='is_active',
            new_name='active',
        ),
    ]
