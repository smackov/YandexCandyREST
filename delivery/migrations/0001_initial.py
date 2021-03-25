# Generated by Django 3.1.7 on 2021-03-25 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('courier_id', models.IntegerField(primary_key=True, serialize=False)),
                ('courier_type', models.CharField(choices=[('foot', 'Foot'), ('bike', 'Bike'), ('car', 'Car')], max_length=4)),
            ],
            options={
                'ordering': ['courier_id', 'courier_type'],
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='WorkingHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='working_hours', to='delivery.courier')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='courier',
            name='regions',
            field=models.ManyToManyField(related_name='couriers', to='delivery.Region'),
        ),
    ]
