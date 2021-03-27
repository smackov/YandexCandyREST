# Generated by Django 3.1.7 on 2021-03-27 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='courier',
            options={'ordering': ['courier_id']},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['order_id']},
        ),
        migrations.AlterModelOptions(
            name='workinghours',
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='DeliveryHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_hours', to='delivery.order')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
