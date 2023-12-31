# Generated by Django 4.2.7 on 2023-11-22 07:32

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iot_device', '0002_remove_device_device_key_device_serial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('values', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot_device.device')),
            ],
        ),
    ]
