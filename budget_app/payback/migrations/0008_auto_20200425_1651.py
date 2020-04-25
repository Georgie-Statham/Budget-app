# Generated by Django 2.1.9 on 2020-04-25 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payback', '0007_auto_20200418_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payback',
            name='currency',
            field=models.CharField(choices=[('GBP', 'GBP'), ('AUD', 'AUD')], default='AUD', max_length=3),
        ),
    ]
