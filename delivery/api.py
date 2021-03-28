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
    CourierIdSerializer,
    OrderSerializer,
    OrderIdSerializer,
    AssignOrderSetSerializer)
from .models import Courier
from .exceptions import OrderAssignBadRequest


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
            orders = serializer.save()
            orders_ids = OrderIdSerializer(orders, many=True)
            response_data = {'orders': orders_ids.data}
            return Response(response_data, status=status.HTTP_201_CREATED)
        
    
class OrdersAssignAPI(APIView):
    """
    Api for assigning orders to the courier.
    
    return AssignOrderSet: orders (notstarted) and assign time.
    """
    
    def get_object(self, pk):
        try:
            courier = Courier.objects.get(courier_id=pk)
        except Courier.DoesNotExist:
            raise OrderAssignBadRequest
        return courier
    
    @transaction.atomic
    def post(self, request):
        serializer = CourierIdSerializer(data=request.data)
        if serializer.is_valid():
            courier = self.get_object(pk=serializer.data['courier_id'])
            order_set = courier.assign_orders()
            if order_set is None:
                return Response([], status=status.HTTP_400_BAD_REQUEST)
            data = AssignOrderSetSerializer(order_set).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
