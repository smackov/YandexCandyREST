"""
API classes.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .serializers import CourierItemPostSerializer
from .models import Courier


class CourierListAPI(APIView):
    """
    Api for creating couriers.
    
    Get list of couriers, valide them and save in db.
    """
    
    @transaction.atomic
    def post(self, request):
        serializer = CourierItemPostSerializer(data=request.data['data'], many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
