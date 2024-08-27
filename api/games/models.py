from django.db import models
from django.contrib.postgres.fields import ArrayField


class Game(models.Model):
    appid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    is_free = models.BooleanField()
    description = models.TextField()
    categories = ArrayField(models.CharField(max_length=255))
    genres = ArrayField(models.CharField(max_length=255))
    release_date = models.DateField()

    def __str__(self):
        return self.name
