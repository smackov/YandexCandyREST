"""
The serializers classes.
"""

from rest_framework import serializers

from .models import Courier, Region, WorkingHours


class RegionSerializer(serializers.ModelSerializer):
    """
    The serializer for Region model.
    """
    
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
    

class TimeIntervalSerializer(serializers.Serializer):
    """
    The serializer represents TimeIntervalAbstract model.
    
    It's used for deserializing data for 'working_hours' field 
    of Courier model.
    """
    
    start = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    end = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
        
    def to_internal_value(self, time_interval: str):
        """
        Change input data to appropriate view.
        
        Get: time_interval: str. Example: '10:00-14:30'
        Return: ret: OrderedDicts([('start': datetime.time), 
                                   ('end': datetime.time)])
        """
        
        start, end = time_interval.split('-')
        item = {
            'start': start,
            'end': end
        }
        ret = super().to_internal_value(item)
        return ret

class CourierItemPostSerializer(serializers.ModelSerializer):
    """
    This serializer is used for posting and creating not existing 
    couriers.
    """
    
    regions = RegionSerializer(many=True)
    working_hours = TimeIntervalSerializer(many=True)
    
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']
        
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
            
        # Create working hours
        for working_hours in validated_data.pop('working_hours'):
            WorkingHours.objects.create(
                start=working_hours['start'],
                end=working_hours['end'],
                courier=courier,
            )
        
        # Save and return courier
        courier.save()
        return courier
