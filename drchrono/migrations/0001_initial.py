# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-08 21:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=255, null=True)),
                ('scheduled_time', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('duration', models.IntegerField(editable=False)),
                ('checkin_time', models.DateTimeField(null=True)),
                ('seen_time', models.DateTimeField(null=True)),
                ('time_waiting', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(editable=False, max_length=255)),
                ('last_name', models.CharField(editable=False, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('date_of_birth', models.DateField(null=True)),
                ('social_security_number', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='drchrono.Doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drchrono.Patient'),
        ),
    ]