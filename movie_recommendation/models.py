from django.db import models

# Create your models here.
class Recommendation(models.Model):
    title = models.MovieTitle
    year = models.IntegerField(default=0)
    genre = models.TextField(default='')
    duration = models.IntegerField(default=0)
    director = models.CharField(max_length=200)
    mainCast = models.TextField(default='')
    recommendationReason = models.TextField(default='')
    predicateScore = models.IntegerField(default=1)


class MovieTitle(models.Model):
    original = models.CharField(max_length=200)
    korean = models.CharField(max_length=200)