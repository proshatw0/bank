# Generated by Django 4.2.13 on 2024-05-20 08:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_number', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='Номер счета')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Баланс')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='Название')),
                ('monthly_cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ежемесячная стоимость')),
            ],
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Процентная ставка')),
                ('is_savings', models.BooleanField(default=False, verbose_name='Вид вклада')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='your_bank.account', verbose_name='Номер счета')),
            ],
        ),
        migrations.CreateModel(
            name='DebitCard',
            fields=[
                ('card_number', models.CharField(max_length=16, primary_key=True, serialize=False, verbose_name='Номер карты')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='your_bank.account', verbose_name='Номер счета')),
                ('subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='your_bank.subscription', verbose_name='Подписка')),
            ],
        ),
    ]