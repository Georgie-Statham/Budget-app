# Generated by Django 2.1.5 on 2019-02-06 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20190127_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='who_for',
            field=models.CharField(choices=[('Claire', 'Claire'), ('Georgie', 'Georgie'), ('Tristan', 'Tristan'), ('Everyone', 'Everyone')], default='Everyone', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='who_paid',
            field=models.CharField(choices=[('Claire', 'Claire'), ('Georgie', 'Georgie'), ('Tristan', 'Tristan')], max_length=10),
        ),
    ]
