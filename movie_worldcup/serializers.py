from rest_framework import serializers
from .models import WorldCupInfo, WorldCupItem

class WorldCupInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorldCupInfo
        fields = ('worldCupId', 'title', 'description', 'totalRound', 'infoImage', 'createdDate')

class WorldCupItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorldCupItem
        fields = ('worldCupId', 'itemId', 'itemImage', 'description')