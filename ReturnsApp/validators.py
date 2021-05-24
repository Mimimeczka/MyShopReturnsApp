from django.core.exceptions import ValidationError
import requests


def validator_check_return_is_summarized(my_return):
    if my_return.summarized:
        raise ValidationError('Cannot modify summarized return')


def validator_check_content_return(return_id):
    my_return_response = requests.get(f'http://127.0.0.1:8004/api/returns/{return_id}/')
    product_in_return = my_return_response.json()
    if not product_in_return['products']:
        raise ValidationError('Cannot summarize empty return')


def validator_check_basket_id(basket_id):
    basket = requests.get(f'http://127.0.0.1:8002/api/basketss/{basket_id}/')
    if not basket:
        raise ValidationError('Basket is not exists')
