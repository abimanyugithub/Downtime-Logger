# Generated by Django 5.1.1 on 2024-09-06 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AndonMachineApp', '0008_alter_mesin_description'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Downtime',
            new_name='DowntimeMesin',
        ),
        migrations.RenameModel(
            old_name='DowntimeByRole',
            new_name='DowntimeRole',
        ),
    ]
