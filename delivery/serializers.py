"""
The serializers classes.
"""

from rest_framework import serializers

from .models import (Courier, Region, WorkingHours, Order, DeliveryHours,
                     AssignedOrderSet, ORDER_WEIGHT_CONSTRAINTS)


class RegionSerializer(serializers.Serializer):
    """
    The serializer for Region model.
    """

    id = serializers.IntegerField()

    def to_internal_value(self, region_id: int):
        """
        Change input data to appropriate view.

        Get: region_id: int
        Return: ret: OrderedDicts(['id': region_id])
        """

        region = {'id': region_id}
        ret = super().to_internal_value(region)
        return ret

    def to_representation(self, instance) -> int:
        """
        Change output data to appropriate view.

        Return `id` of region as integer. In default it returns 
        OrderedDict([('id', int)]).
        """

        ret = super().to_representation(instance)
        return ret['id']


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

    def to_representation(self, instance) -> str:
        """
        Change output data to appropriate view.

        Return working hours as str in format '%H:%M'. 
        In default it returns for example: 
        OrderedDict([('start', '09:00'), ('end', '11:00')]).
        """

        return str(instance)


class CourierItemPostSerializer(serializers.ModelSerializer):
    """
    This serializer is used for posting and creating not existing 
    couriers.
    """

    regions = RegionSerializer(many=True, write_only=True)
    working_hours = TimeIntervalSerializer(many=True, write_only=True)

    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']
        extra_kwargs = {'courier_type': {'write_only': True}}

    def create(self, validated_data):
        """
        Create courier, his regions (if they don't exist), his working hours.
        """

        # Create courier
        courier = Courier.objects.create(
            courier_id=validated_data.pop('courier_id'),
            courier_type=validated_data.pop('courier_type'),
        )

        # Create regions
        regions = validated_data.pop('regions')
        for region_data in regions:
            region, _ = Region.objects.get_or_create(**region_data)
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

    def to_representation(self, instance):
        """
        Change output data to appropriate view.

        Rename field 'courier_id' to 'id'. 
        """
        ret = super().to_representation(instance)
        ret['id'] = ret.pop('courier_id')
        return ret


class CourierItemPatchSerializer(serializers.ModelSerializer):
    """
    This serializer is used for patching (update) existing couriers.
    """

    regions = RegionSerializer(many=True, required=False)
    working_hours = TimeIntervalSerializer(many=True, required=False)

    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']
        extra_kwargs = {
            'courier_type': {'required': False},
            'courier_id': {'read_only': True},
        }

    def update(self, instance, validated_data):
        """
        Update and return an existing `Courier` instance.
        """

        # Set new 'courier_type' if it presents in validated_data
        instance.courier_type = validated_data.get(
            'courier_type', instance.courier_type)

        # If regions: unset old regions from instance and set new regions
        regions = validated_data.get('regions')
        if regions:

            # Unset all old regions
            instance.regions.set([])

            # Set all new regions to the instance
            for region in regions:
                region_id, _ = Region.objects.get_or_create(id=region['id'])
                instance.regions.add(region_id)

        # If working hours: delete old working hours and create new ones
        working_hours = validated_data.get('working_hours')
        if working_hours:

            # Delete old working hours instances that belong to the courier
            for working_hours_instance in instance.working_hours.all():
                working_hours_instance.delete()

            # Create new working hours
            for working_hours_item in working_hours:
                WorkingHours.objects.create(
                    start=working_hours_item['start'],
                    end=working_hours_item['end'],
                    courier=instance)

        # Save, refresh notstarted orders (if they are) and return courier
        instance.save()
        instance.remove_unsuitable_orders()
        return instance


class CourierDetailSerializer(serializers.ModelSerializer):
    """
    This serializer for a detailed display of a specific courier.
    """

    regions = RegionSerializer(many=True)
    working_hours = TimeIntervalSerializer(many=True)

    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']
        read_only_fields = ['courier_id',
                            'courier_type', 'regions', 'working_hours']

    def to_representation(self, instance):
        """
        Add two additional fields:

        - rating (if courier have at least one finished order)
        - earnings
        """

        ret = super().to_representation(instance)

        # Add the rating field if the courier have finished order(-s)
        rating = instance.rating
        if rating:
            ret['rating'] = rating

        # Add earnings field
        ret['earnings'] = instance.earnings
        return ret


class CourierIdSerializer(serializers.Serializer):
    """
    The serializer for getting posts with one field: 'courier_id'
    """

    courier_id = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    """
    This serializer is used for posting and creating not existing 
    orders.
    """

    region = RegionSerializer(write_only=True)
    delivery_hours = TimeIntervalSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'weight', 'region', 'delivery_hours']
        extra_kwargs = {
            'weight': {'write_only': True,
                       **ORDER_WEIGHT_CONSTRAINTS, },
        }

    def create(self, validated_data):

        # Create or get Region if it exists
        region, _ = Region.objects.get_or_create(
            id=validated_data.pop('region')['id'])

        # Create Order instance
        order = Order.objects.create(
            order_id=validated_data.pop('order_id'),
            weight=validated_data.pop('weight'),
            region=region,
        )
        # Create delivery hours instances
        for delivery_hours_item in validated_data.pop('delivery_hours'):
            DeliveryHours.objects.create(
                start=delivery_hours_item['start'],
                end=delivery_hours_item['end'],
                order=order,
            )
        return order


class OrderIdSerializer(serializers.ModelSerializer):
    """
    The serializer for Order model with only one field: 'order_id'.
    """

    class Meta:
        model = Order
        fields = ['order_id']
        read_only_fields = ['order_id']

    def to_representation(self, instance):
        """
        Change output data to appropriate view.

        Rename field 'order_id' to 'id'. 
        """
        ret = super().to_representation(instance)
        ret['id'] = ret.pop('order_id')
        return ret


class AssignOrderSetSerializer(serializers.ModelSerializer):
    """
    The serializer for AssignOrderSet model.
    """

    notstarted_orders = OrderIdSerializer(many=True, read_only=True)

    class Meta:
        model = AssignedOrderSet
        fields = ['notstarted_orders', 'assign_time']
        read_only_fields = ['notstarted_orders', 'assign_time']

    def to_representation(self, instance):
        """
        Change output data to appropriate view.

        Rename field 'notstarted_orders' to 'orders'. 
        """
        ret = super().to_representation(instance)
        ret['orders'] = ret.pop('notstarted_orders')
        # Move to end assign_time in the representation view
        ret.move_to_end('assign_time')
        return ret


class CompleteOrderSerializer(serializers.Serializer):
    """
    The serializer for getting complete order posts.
    """

    courier_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    complete_time = serializers.DateTimeField()
