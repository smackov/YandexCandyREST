"""
API classes.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.db import transaction

from .serializers import (
    CourierItemPostSerializer,
    CourierItemPatchSerializer,
    OrderSerializer)
from .models import Courier


class CourierListAPI(APIView):
    """
    Api for creating couriers.

    Get list of couriers, valide them and save in db.
    """

    @transaction.atomic
    def post(self, request):
        serializer = CourierItemPostSerializer(
            data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = {'couriers': serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)


class CourierItemAPI(APIView):
    """
    Api for updating courier instance.

    Get courier properties, valide them and update the courier.
    """
    
    def get_object(self, pk):
        try:
            courier = Courier.objects.get(courier_id=pk)
        except Courier.DoesNotExist:
            raise Http404
        return courier

    @transaction.atomic
    def patch(self, request, pk):
        courier = self.get_object(pk=pk)
        serializer = CourierItemPatchSerializer(courier, data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListAPI(APIView):
    """
    Api for creating orders.

    Get list of orders, valide them and save in db.
    """

    @transaction.atomic
    def post(self, request):
        serializer = OrderSerializer(
            data=request.data['data'], many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = {'orders': serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)
