# Generated by Django 2.1.5 on 2019-01-27 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20190120_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('Food', 'Food'), ('Baby', 'Baby'), ('Fun_with_friends', 'Fun with friends'), ('Fun_with_each_other', 'Fun with each other'), ('Health', 'Pharmacy/Health'), ('Hobbies', 'Hobbies'), ('Rent', 'Rent'), ('Bills', 'Utility bills'), ('Clothes', 'Clothes'), ('Household', 'Household'), ('Cat', 'Cat'), ('Transport', 'Transport'), ('Travel', 'Travel'), ('Misc', 'Miscellaneous')], default='Food', max_length=20),
        ),
    ]
