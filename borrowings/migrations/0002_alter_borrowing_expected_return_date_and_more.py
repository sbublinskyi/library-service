# Generated by Django 4.1.3 on 2022-11-30 14:35

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="expected_return_date",
            field=models.DateField(default=datetime.date(2022, 12, 14)),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="borrowings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]