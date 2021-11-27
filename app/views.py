from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import *

#utils.py contains details version of store, cart & checkout methods code

#store methods

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all() #products query
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'app/Store.html', context)

#cart methods
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, "order": order, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'app/Cart.html', context)

#checkout methods
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, "order": order, 'cartItems': cartItems}
    return render(request, 'app/Checkout.html', context)

#cart items update methods
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # print('Action:', action)
    # print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("item was added.", safe=False)

#order processing & payment
def processOrder(request):
    # print('data: ', request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('payment complete!', safe=False)
