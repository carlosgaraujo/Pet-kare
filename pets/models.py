from django.db import models

from groups.models import Group
from traits.models import Trait


class Sex(models.TextChoices):
    MALE = 'Male',
    FEMALE = "Female",
    DEFAULT = 'Not Informed',


class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.FloatField()
    sex = models.CharField(max_length=20, choices=Sex.choices,
                           default=Sex.DEFAULT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT,
                              related_name="pets")
    traits = models.ManyToManyField(Trait, related_name="pets")


def __repr__(self):
    return f'{self.id} - {self.name}'
