from django.contrib import admin
from .models import WorldCupInfo, WorldCupItem

# Register your models here.
admin.site.register(WorldCupInfo)
admin.site.register(WorldCupItem)