# Generated by Django 2.1.5 on 2019-04-26 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20190219_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='currency',
            field=models.CharField(choices=[('ILS', 'ILS'), ('GBP', 'GBP'), ('AUD', 'AUD')], default='ILS', max_length=3),
        ),
    ]
