# Generated by Django 2.1.9 on 2020-04-18 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20191123_0736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('Food', 'Food'), ('Robin', 'Robin'), ('Fun_with_friends', 'Fun with friends'), ('Fun_with_each_other', 'Fun with each other'), ('Health', 'Pharmacy/Health'), ('Hobbies', 'Hobbies'), ('Rent', 'Rent'), ('Bills', 'Utility bills'), ('Clothes', 'Clothes'), ('Household', 'Household'), ('Cat', 'Cat'), ('Transport', 'Transport'), ('Holidays', 'Holidays'), ('Gifts', 'Gifts and donations'), ('Misc', 'Miscellaneous')], default='Food', max_length=20),
        ),
    ]
