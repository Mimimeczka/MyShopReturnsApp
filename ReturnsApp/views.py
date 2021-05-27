from .serializers import ReturnSerializer
from rest_framework import viewsets
from .models import Return, Product
from rest_framework.response import Response
from datetime import date
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
import requests
from rest_framework import status
from .validators import validator_check_content_return, validator_check_return_is_summarized, validator_check_basket_id


class ReturnViewSet(viewsets.ModelViewSet):
    # queryset = Product.objects.all()
    serializer_class = ReturnSerializer

    def get_queryset(self):
        _return = Return.objects.all()
        return _return

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ReturnSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ReturnSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        validator_check_basket_id(request.query_params['basket_id'])
        my_return = Return.objects.create(
            date=date.isoformat(date.today()),
            sum=0,
            basket_id=request.query_params['basket_id']
        )
        serializer = ReturnSerializer(my_return, many=False)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return Response('Cannot update return')

    def destroy(self, request, *args, **kwargs):
        return Response('Cannot delete return')


def change_return_value(my_return, quantity, product_from_response, operation):
    previous_sum_return = float(my_return.sum)
    products_sum = float(quantity) * float(product_from_response['price'])
    if operation == 'add':
        actual_sum_return = previous_sum_return + products_sum
    elif operation == 'delete':
        actual_sum_return = previous_sum_return - products_sum
    else:
        return Response('Wrong action', status=status.HTTP_401_UNAUTHORIZED)
    my_return.sum = actual_sum_return
    my_return.save()
    return my_return


@api_view(['POST'])
def add_product_to_return(request, return_id, product_id):

    my_return = get_object_or_404(Return, id=return_id)
    validator_check_return_is_summarized(my_return)
    response = requests.get(f'http://127.0.0.1:8001/api/products/{product_id}/')
    if response.status_code == 404:
        return Response('Product not found', status=status.HTTP_404_NOT_FOUND)

    product_from_response = response.json()
    quantity = request.data['quantity']

    my_return_response = requests.get(f'http://127.0.0.1:8004/api/returns/{return_id}/')
    product_in_return = my_return_response.json()

    for product in product_in_return['products']:
        if product['product_id'] == product_id:
            product_to_update = Product.objects.get(id=product['id'])
            to_add = int(product_to_update.quantity) + int(quantity)
            product_to_update.quantity = int(to_add)
            product_to_update.save()
            break

    else:
        Product.objects.create(
            product_id=int(product_from_response['id']),
            quantity=int(quantity),
            my_return=my_return
        )

    change_return_value(my_return, quantity, product_from_response, 'add')

    serializer = ReturnSerializer(my_return, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def delete_product_from_return(request, return_id, product_id):

    my_return = get_object_or_404(Return, id=return_id)
    validator_check_return_is_summarized(my_return)
    response = requests.get(f'http://127.0.0.1:8001/api/products/{product_id}/')
    product_from_response = response.json()
    quantity = request.data['quantity']

    my_return_response = requests.get(f'http://127.0.0.1:8004/api/returns/{return_id}/')
    product_in_return = my_return_response.json()

    access = False

    for product in product_in_return['products']:
        if product['product_id'] == product_id:
            access = True
            product_to_update = Product.objects.get(id=product['id'])
            to_update = int(product_to_update.quantity) - int(quantity)
            if to_update > 0:
                product_to_update.quantity = int(to_update)
                product_to_update.save()
            elif to_update < 0:
                return Response('Cannot remove more product than you have', status=status.HTTP_401_UNAUTHORIZED)
            elif to_update == 0:
                product_to_update.delete()
            else:
                return Response('Wrong value', status=status.HTTP_401_UNAUTHORIZED)
            break

    if not access:
        return Response('Cannot remove product which is not in the return', status=status.HTTP_401_UNAUTHORIZED)

    change_return_value(my_return, quantity, product_from_response, 'delete')

    serializer = ReturnSerializer(my_return, many=False)
    return Response(serializer.data)


def change_product_value(product_id, quantity):
    product_response = requests.get(f'http://127.0.0.1:8001/api/products/{product_id}/')
    my_product = product_response.json()
    update_product_quantity = my_product['quantity'] + quantity
    requests.put(f'http://127.0.0.1:8001/api/products/{product_id}/', data={
        'name': '',
        'description': '',
        'price': '',
        'quantity': update_product_quantity
    })


@api_view(['GET'])
def summarize_return(request, return_id):
    my_return = get_object_or_404(Return, id=return_id)
    validator_check_return_is_summarized(my_return)
    validator_check_content_return(return_id)

    return_response = requests.get(f'http://127.0.0.1:8004/api/returns/{return_id}/')
    my_return_json = return_response.json()
    product_in_return = my_return_json['products']

    basket_in_return = my_return_json['basket_id']
    basket_response = requests.get(f'http://127.0.0.1:8002/api/baskets/{basket_in_return}/')
    basket_json = basket_response.json()

    product_in_basket = basket_json['products']

    fault = True
    for basket_product in product_in_basket:
        for return_product in product_in_return:
            if basket_product['product_id'] == return_product['product_id']:
                if basket_product['quantity'] < return_product['quantity']:
                    break
                fault = False
        break

    if fault:
        raise Exception('You can not return this products')

    for product in my_return_json['products']:
        change_product_value(product['product_id'], product['quantity'])

    my_return.summarized = True
    my_return.save()
    serializer = ReturnSerializer(my_return, many=False)
    return Response(serializer.data)