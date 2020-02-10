# Generated by Django 2.1.9 on 2019-11-23 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20190426_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='currency',
            field=models.CharField(choices=[('ILS', 'ILS'), ('GBP', 'GBP'), ('AUD', 'AUD')], default='AUD', max_length=3),
        ),
        migrations.AlterField(
            model_name='expense',
            name='who_for',
            field=models.CharField(choices=[('Tristan', 'Tristan'), ('Claire', 'Claire'), ('Georgie', 'Georgie'), ('Everyone', 'Everyone')], default='Everyone', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='who_paid',
            field=models.CharField(choices=[('Tristan', 'Tristan'), ('Claire', 'Claire'), ('Georgie', 'Georgie')], max_length=10),
        ),
    ]
