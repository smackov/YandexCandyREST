"""
The serializers classes.
"""

from rest_framework import serializers
from rich import print

from .models import Courier, Region, WorkingHours


class RegionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Region
        fields ='__all__'
        
    def to_internal_value(self, region_id: int):
        """
        Change input data to appropriate view.
        
        Get: region_id: int
        Return: ret: OrderedDicts(['id': region_id])
        """
        region = {'id': region_id}
        ret = super().to_internal_value(region)
        return ret


class CourierItemPostSerializer(serializers.ModelSerializer):
    """
    This serializer is used for posting and creating not existing 
    couriers.
    """
    
    regions = RegionSerializer(many=True)
    
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions']
        
    def create(self, validated_data):
        # Create courier
        courier = Courier.objects.create(
            courier_id=validated_data.pop('courier_id'),
            courier_type=validated_data.pop('courier_type'),
        )
        
        # Create regions
        regions = validated_data.pop('regions')
        for region_data in regions:
            region = Region.objects.create(**region_data)
            # Set region to current courier
            courier.regions.add(region)
        
        # Save and return courier
        courier.save()
        return courier
