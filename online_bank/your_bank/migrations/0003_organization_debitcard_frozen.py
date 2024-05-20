# Generated by Django 4.2.13 on 2024-05-20 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('your_bank', '0002_alter_debitcard_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='your_bank.account', verbose_name='Номер счета')),
                ('name', models.CharField(max_length=100, verbose_name='Название организации')),
            ],
        ),
        migrations.AddField(
            model_name='debitcard',
            name='frozen',
            field=models.BooleanField(default=False, verbose_name='Заморожена'),
        ),
    ]
