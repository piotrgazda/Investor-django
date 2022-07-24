# Generated by Django 4.0.4 on 2022-05-17 22:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0002_alter_company_abbreviation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='price',
            name='date',
            field=models.DateField(db_index=True),
        ),
        migrations.CreateModel(
            name='UserStockInvestments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('price', models.FloatField()),
                ('date', models.DateField(db_index=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.currency')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IncomeStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('period', models.CharField(choices=[('quaterly', 'quaterly'), ('annual', 'annual')], max_length=20)),
                ('sales', models.FloatField()),
                ('cost_of_goods', models.FloatField()),
                ('gross_profit', models.FloatField()),
                ('sga', models.FloatField()),
                ('netto_income', models.FloatField()),
                ('diluted_eps', models.FloatField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CashStatements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('period', models.CharField(choices=[('quaterly', 'quaterly'), ('annual', 'annual')], max_length=20)),
                ('netto_income', models.FloatField()),
                ('operating', models.FloatField()),
                ('investing', models.FloatField()),
                ('issuance_stock', models.FloatField()),
                ('cash', models.FloatField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BalanceStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('period', models.CharField(choices=[('quaterly', 'quaterly'), ('annual', 'annual')], max_length=20)),
                ('assets', models.FloatField()),
                ('liabilities', models.FloatField()),
                ('bvps', models.FloatField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='price',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stocks.currency'),
        ),
        migrations.CreateModel(
            name='CurrencyExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField()),
                ('date', models.DateField(db_index=True)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.currency')),
            ],
            options={
                'unique_together': {('currency', 'date')},
            },
        ),
    ]