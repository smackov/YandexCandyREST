# Generated by Django 3.1.7 on 2021-03-27 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_auto_20210327_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
    ]
