from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist


def _cart_id(request):
    session_cart = request.session.session_key
    if not session_cart:
        session_cart = request.session.create()
    return session_cart


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
    cart_item.save()
    return redirect('cart')


def remove_from_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def cart(request, sub_total=0, tax=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            sub_total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = 1000  # TODO needs to be calculated here
    except ObjectDoesNotExist:
        pass  # ignore this exception as it does not affect usability

    context = {
        'sub_total' : sub_total,
        'quantity'  : quantity,
        'cart_items': cart_items,
        'tax'       : tax,
        'total'     : sub_total + tax
    }
    return render(request, 'store/cart.html', context)
