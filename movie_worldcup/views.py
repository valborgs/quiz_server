from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import WorldCupInfo, WorldCupItem
from .serializers import WorldCupInfoSerializer, WorldCupItemSerializer
import datetime

# Create your views here.
@api_view(['GET'])
def monthlyWorldCupInfo(request, year, month):
    if not year or not month: 
        return Response({"error": "year and month parameters are required."}, status=400)
    
    try: 
        year = int(year) 
        month = int(month) 
        startDate = datetime.date(year, month, 1) 
        endDate = datetime.date(year, month + 1, 1) if month < 12 else datetime.date(year + 1, 1, 1) 
        worldCupInfo = WorldCupInfo.objects.filter( Q(createdDate__gte=startDate) & Q(createdDate__lt=endDate) )
        if(len(worldCupInfo)<1):
            return Response({"error": "worldCupInfo is empty"}, status=400)
        serializer = WorldCupInfoSerializer(worldCupInfo, many=True) 
        return Response(serializer.data) 
    except ValueError: 
        return Response({"error": "Invalid year or month format."}, status=400) 
    except Exception as e: 
        return Response({"error": str(e)}, status=500)
    

@api_view(['GET'])
def monthlyWorldCupItems(request, worldCupId):
    if not worldCupId: 
        return Response({"error": "worldCupId parameters are required."}, status=400)
    
    try:
        worldCupItems = WorldCupItem.objects.filter(worldCupId=worldCupId)
        if(len(worldCupItems)<1):
            return Response({"error": "worldCupItems are empty"}, status=400)
        serializer = WorldCupItemSerializer(worldCupItems, many=True)
        return Response(serializer.data)
    except ValueError: 
        return Response({"error": "Invalid year or month format."}, status=400) 
    except Exception as e: 
        return Response({"error": str(e)}, status=500)

