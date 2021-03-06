"""
The models.
"""

import collections
from typing import Optional, Tuple
from operator import attrgetter

from django.db import models
from django.core.exceptions import FieldError


COURIER_TYPES = [
    ('foot', 'Foot'),
    ('bike', 'Bike'),
    ('car', 'Car'),
]

COURIER_LOAD_CAPACITY = {
    'foot': 10,
    'bike': 15,
    'car': 50,
}

ORDER_WEIGHT_CONSTRAINTS = {
    # Minimum validated value is 0.01 after deserialization
    'min_value': 0.009,
    'max_value': 50,
}

RATE_OF_PAYMENT = {
    'foot': 2,
    'bike': 5,
    'car': 9,
}


class Courier(models.Model):
    """
    The courier is the man delivering orders to customers.
    """

    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=4, choices=COURIER_TYPES)
    regions = models.ManyToManyField('Region', related_name='couriers')
    current_set_of_orders = models.ForeignKey(
        'AssignedOrderSet',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+')
    # The realted_name is '+' because it will never be used.

    class Meta:
        ordering = ['courier_id']

    def __str__(self):
        return 'Courier(id={}, type={}, regions={})'.format(
            self.courier_id, self.courier_type, list(self.regions.all()),
        )

    @property
    def load_capacity(self):
        """
        The load capacity is the maximum weight Courier is able to deliver.

        It matches the constants: COURIER_TYPES, COURIER_LOAD_CAPACITY
        """

        load = COURIER_LOAD_CAPACITY.get(self.courier_type)
        if load:
            return load
        raise FieldError("The 'courier_type' field of Courier with "
                         f"courier_id={self.courier_id} contains the "
                         f"unresolved value='{self.courier_type}' that "
                         "absents in COURIER_LOAD_CAPACITY")

    @property
    def rating(self) -> float:
        """
        The rating of courier.

        Formule:
        rating = (60*60 - min(t, 60*60))/(60*60) * 5
        t = min(td[1], td[2], ..., td[n])
          where 
        td [i] - average time of order delivery for region i (in seconds).
        """

        # Get all finished orders by the current courier
        orders = self.get_finished_orders()

        # If courier doesn't have completed orders - return None
        if orders.count() == 0:
            return None

        # Find the minimum average time for all districts and calculate rating
        t = self._calculate_minimum_average_time_for_all_regions(orders=orders)
        rating = (60*60 - min(t, 60*60))/(60*60) * 5
        return round(rating, 2)

    @property
    def earnings(self) -> int:
        """
        The sum of money that the current courier gained.
        """

        # Get all finished orders by the current courier
        orders = self.get_finished_orders()

        # If courier doesn't have completed orders - return zero
        if orders.count() == 0:
            return 0

        # Find the sum of all money that the courier gained
        order_payments = []
        for order in orders:
            rate = RATE_OF_PAYMENT.get(order.set_of_orders.courier_type)
            payment = 500 * rate
            order_payments.append(payment)
        return sum(order_payments)

    def assign_orders(self) -> Optional['AssignedOrderSet']:
        """
        Find the appropriate orders and assign them to the courier.
        """

        # If the courier has unfinished orders in `current_set_of_orders`,
        # then return `current_set_of_orders`.
        if self.current_set_of_orders:
            if self.current_set_of_orders.notstarted_orders.count() != 0:
                return self.current_set_of_orders

        # If the courier doesn't have `current_set_of_orders` or has, but
        # its unfinished orders are over, then create new AssignedOrderSet
        # for the courier and return it.
        orders = self.find_matching_orders()
        if orders:
            # Create new AssignedOrderSet and pin it to the courier
            self.current_set_of_orders = AssignedOrderSet.objects.create(
                courier=self, courier_type=self.courier_type)
            self.save()
            # All the matching orders put in notstarted_orders stack
            self.current_set_of_orders.notstarted_orders.set(orders)
            # Set new order set to each order in orders
            for order in orders:
                order.set_of_orders = self.current_set_of_orders
                order.save()
            return self.current_set_of_orders

        # But if we can't find appropriate
        # orders, then return None.
        return None

    def find_matching_orders(self, queryset=None):
        """
        Find the matching orders that mathes by parameters: 
        region, weight and delivery/working hours.
        """

        # If queryset is None -> get all orders
        # Queryset may isn't None when the properties of the courier are
        # being changed and the queryset would be the all notstarted orders
        if queryset is None:
            queryset = Order.objects.all()
            
            # We here if we attempt assign orders to the courier
            # then any order hasn't be included in active assign_set
            queryset = queryset.filter(set_of_orders=None)

        # Weight of each order has to be less or equal Courier's load capacity
        orders = queryset.filter(weight__lte=self.load_capacity)

        # Orders hasn't had been completed already
        orders = orders.filter(complete_time=None)

        # Region of order has to be in courier list of regions he works in
        orders = orders.filter(region__in=self.regions.all())

        # Orders has to have time intersections beetwen delivery hours and
        # Courier's working hours
        orders = self._filter_orders_by_delivery_hours(orders=orders)

        return orders

    def get_finished_orders(self):
        """
        Return all the orders that are finished and belong the courier.
        """

        # Find all completed orders
        orders = Order.objects.filter(complete_time__isnull=False)

        # Filter orders completed by the current courier
        orders = orders.filter(set_of_orders__courier=self)
        return orders

    def remove_unsuitable_orders(self):
        """
        When the courier parameters are being changed and

        the courier has notstarted orders, it method is being called.
        The method remove unsuitable order from notstarted orders set.
        """
        
        # If the courier doesn't have assigned orders -> Do nothing
        if not self.current_set_of_orders:
            return None

        notstarted_orders = self.current_set_of_orders.notstarted_orders.all()
        suitable_notstarted_orders = self.find_matching_orders(
            queryset=notstarted_orders)
        
        # Unset set_of_orders of unsuitable_notstarted_orders
        for order in notstarted_orders:
            if not order in suitable_notstarted_orders:
                order.set_of_orders = None
                order.save()
        
        # Set only suitable orders
        self.current_set_of_orders.notstarted_orders.set(
            suitable_notstarted_orders)

    def _filter_orders_by_delivery_hours(self, orders):
        """
        Returns matching orders from initial QuerySet: orders.
        """

        matching_orders = []
        for order in orders:
            # Have we any intersections in all working hours
            # of courier and delivery hours of order?
            if self._is_suitable_delivery_hours(order=order):
                matching_orders.append(order)
        return matching_orders

    def _is_suitable_delivery_hours(self, order) -> bool:
        """
        If find at least 1 intersection in in all working hours
        of courier and delivery hours of order - return True.
        Else: return False
        """
        for delivery_hours in order.delivery_hours.all():
            if self._have_intersection(delivery_hours):
                return True
        return False

    def _have_intersection(self, delivery_hours) -> bool:
        """
        Find the time intersections in given delivery hours (1 item)
        and working hours of courier (many items).
        """

        # Separate working hours to them starts and ends
        # it is necessary for comparison of times
        courier_starts, courier_ends = [], []
        for working_hours in self.working_hours.all():
            courier_starts.append(working_hours.start)
            courier_ends.append(working_hours.end)

        # Give more brief names to delivery hours
        order_start = delivery_hours.start
        order_end = delivery_hours.end

        # check each time matching option
        for courier_start, courier_end in zip(courier_starts, courier_ends):
            # if we have a partial intersection at least 1 minute
            if (courier_start < order_start < courier_end
                    or courier_start < order_end < courier_end):
                return True
            # If all working hours into delivery hours
            elif order_start <= courier_start and order_end >= courier_end:
                return True

        # The time intersections don't exist
        return False

    def _calculate_minimum_average_time_for_all_regions(self, orders) -> int:
        """
        Find the minimum average time in seconds for all districts.

        t = min(td[1], td[2], ..., td[n])
          where 
        td [i] - average time of order delivery for region i (in seconds).
        """

        # Sort orders by regions
        regions = collections.defaultdict(list)
        for order in orders:
            regions[order.region].append(order)

        # For each region find average times
        average_times = []
        for order_list in regions.values():
            time = self._find_average_time_for_orders(orders=order_list)
            average_times.append(time)

        # Find and return the minimum average time for all districts
        return min(average_times)

    def _find_average_time_for_orders(self, orders) -> int:
        """
        Given a list of orders. Find average delivery time in seconds.
        """

        # The orders must be sorted by 'complete_time' field
        orders = sorted(orders, key=attrgetter('complete_time'))

        # Time of first order calculates with another formule
        # It's delta of assign_time and complete_time
        order = orders[0]
        time = order.complete_time - order.set_of_orders.assign_time
        time = time.total_seconds()

        # If we have only 1 order
        if len(orders) == 1:
            return round(time)

        # If we have more than 1 order
        times = [time]
        for index, order in enumerate(orders[1:], start=1):
            time = order.complete_time - orders[index-1].complete_time
            times.append(time.total_seconds())

        # Return average_time in seconds
        # (e.g. 30 or 48.23899 with microseconds)
        average_time = sum(times) / len(times)
        return round(average_time)


class Order(models.Model):
    """
    The Order model.
    """

    order_id = models.IntegerField(primary_key=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2)
    region = models.ForeignKey(
        'Region',
        on_delete=models.CASCADE,
        related_name='orders')
    complete_time = models.DateTimeField(blank=True, null=True)
    set_of_orders = models.ForeignKey(
        'AssignedOrderSet',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)

    class Meta:
        ordering = ['order_id']

    def __str__(self):
        return 'Order (order_id={}, weight={}, region={})'.format(
            self.order_id, self.weight, self.region.id)

    def complete(self, courier, complete_time) -> Tuple[bool, str]:
        """
        Complete the order. 

        Fill out complete_time.
        """

        # If the order was not assigned
        if not self.set_of_orders:
            return False, 'The order was not assigned'

        # If the order was assigned to another courier
        if self.set_of_orders.courier != courier:
            return False, 'The order was assigned to another courier'

        # If data is valid:
        # Write compete time
        self.complete_time = complete_time
        self.save()
        # Move order from notstarted_orders to finished_orders
        # in its set_or_orders
        self.set_of_orders.notstarted_orders.remove(self)
        self.set_of_orders.finished_orders.add(self)

        return True, 'OK'


class AssignedOrderSet(models.Model):
    """
    This is a collection of orders assigned to a specific courier.

    When orders are successfully assigned to the courier, a new set
    of assigned orders is submitted (this model).
    """

    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE, related_name='all_assigned_sets')
    courier_type = models.CharField(
        max_length=4, choices=COURIER_TYPES)
    assign_time = models.DateTimeField(auto_now=True)
    notstarted_orders = models.ManyToManyField(
        Order, related_name='sets_with_notstarted_status')
    finished_orders = models.ManyToManyField(Order)

    def __str__(self):
        return 'Order set (id={}, courier_id={})'.format(
            self.id, self.courier.courier_id)


class Region(models.Model):
    """
    The region of a city is represented as a number.
    """
    id = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return 'Region ({})'.format(self.id)

    def __repr__(self):
        return str(self.id)


class TimeIntervalAbstract(models.Model):
    """
    The abstract class are inhereted by WorkingHours.

    Has 2 fields: 
        start: datetime.time
        end: datetime.time
    """

    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        abstract = True
        ordering = ['id']

    def __str__(self):
        return '{}-{}'.format(
            self.start.strftime('%H:%M'),
            self.end.strftime('%H:%M'),
        )


class WorkingHours(TimeIntervalAbstract):
    """"
    The WorkingHours class represent 'working_hours' field of Courier model.

    The format of 'working_hours' is 'HH:MM-HH:MM'
    Example: '09:00-12:00'
    """

    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE, related_name='working_hours',
    )


class DeliveryHours(TimeIntervalAbstract):
    """"
    The DeliveryHours class represent 'delivery_hours' field of Order model.

    The format of 'delivery_hours' is 'HH:MM-HH:MM'
    Example: '09:00-12:00'
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='delivery_hours',
    )
