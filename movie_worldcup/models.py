from django.db import models

# Create your models here.
class WorldCupInfo(models.Model):
    worldCupId = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField('')
    totalRound = models.IntegerField(default=4)
    infoImage = models.ImageField(upload_to='images/info/', blank=True)
    createdDate = models.DateField(auto_now=True)

class WorldCupItem(models.Model):
    worldCupId = models.ForeignKey(WorldCupInfo, on_delete=models.CASCADE)
    itemId = models.AutoField(primary_key=True, unique=True)
    itemImage = models.ImageField(upload_to='images/items/', blank=True)
    description = models.CharField(max_length=200)