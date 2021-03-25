"""
The serializers classes.
"""

from rest_framework import serializers

from .models import Courier, Region, WorkingHours


class RegionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Region
        fields ='__all__'


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
        
    def to_internal_value(self, data):
        # Change in input data representing of 'regions' field
        # from 'regions' = [1, 2] to 'regions' = [{'id': 1}, {'id': 2}]
        regions = []
        for region_id in data['regions']:
            regions.append({'id': region_id})
        data['regions'] = regions
            
        return super().to_internal_value(data)
