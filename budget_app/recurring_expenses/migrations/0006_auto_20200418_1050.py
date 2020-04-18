# Generated by Django 2.1.9 on 2020-04-18 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recurring_expenses', '0005_auto_20200418_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurring',
            name='currency',
            field=models.CharField(choices=[('GBP', 'GBP'), ('AUD', 'AUD')], default='AUD', max_length=3),
        ),
    ]
