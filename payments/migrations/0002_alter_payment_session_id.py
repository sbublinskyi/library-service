# Generated by Django 4.1.3 on 2022-11-30 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="session_id",
            field=models.CharField(max_length=255),
        ),
    ]
