"""
The utils.
"""

from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from django.urls import reverse


class OrderAssignBadRequest(APIException):
    status_code = 400
    default_detail = "Courier doesn't exist"
    default_code = 'Bad request'


class NoDataProvidedBadRequest(APIException):
    status_code = 400
    default_detail = "No data provided"
    default_code = 'Bad request'
    

def validate_exception_handler(exc, context):
    """
    It's exception handler is used for creating awesome structure

    of errors that happens in validation time.
    """

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    
    # check that a ValidationError exception is raised
    if isinstance(exc, ValidationError):
        path = context['request'].stream.path
        if path == reverse('couriers'):
            response = couriers_exception_handler(response, context)
        elif path == reverse('orders'):
            response = orders_exception_handler(response, context)

    return response


def couriers_exception_handler(response, context):
    """
    The courier exception handler.
    """
    
    request_data = context['request'].data['data']
    
    # Create new formated data
    formated_data = []
    for courier_data, initial_errors in zip(request_data, response.data):
        courier_id = courier_data.get('courier_id')
        if courier_id and initial_errors:
            error_dict = {'id': courier_id}
            error_dict.update(initial_errors)
            formated_data.append(error_dict)
    
    # Wrap all response formated data (errors messages) into dict
    # with key 'validation_error' and 'couriers'
    response.data = {
        'validation_error': {'couriers': formated_data},
    }
    return response


def orders_exception_handler(response, context):
    """
    The order exception handler.
    """
    
    request_data = context['request'].data['data']
    
    # Create new formated data
    formated_data = []
    for order_data, initial_errors in zip(request_data, response.data):
        order_id = order_data.get('order_id')
        if order_id and initial_errors:
            error_dict = {'id': order_id}
            error_dict.update(initial_errors)
            formated_data.append(error_dict)
    
    # Wrap all response formated data (errors messages) into dict
    # with key 'validation_error' and 'orders'
    response.data = {
        'validation_error': {'orders': formated_data},
    }
    return response
    