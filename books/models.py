from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models


def validate_positive(value):
    if value < 0:
        raise ValidationError(
            _(f"{value} is not a positive number"),
            params={"value": value},
        )


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "H", _("Hard")
        SOFT = "S", _("Soft")
    title = models.CharField(max_length=63, unique=True)
    author = models.CharField(max_length=63)
    cover = models.CharField(choices=Cover.choices)
    inventory = models.IntegerField(validators=[validate_positive])
    daily_fee = models.DecimalField(validators=[validate_positive])

    def __str__(self):
        return self.title
