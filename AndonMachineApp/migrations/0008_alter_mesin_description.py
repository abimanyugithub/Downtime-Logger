# Generated by Django 5.1.1 on 2024-09-06 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AndonMachineApp', '0007_alter_mesin_no_machine'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mesin',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
