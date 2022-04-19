from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product, Variant
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist


def _cart_id(request):
    session_cart = request.session.session_key
    if not session_cart:
        session_cart = request.session.create()
    return session_cart


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variants = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST.get(key)
            try:
                variant = Variant.objects.get(product=product, variant_category__iexact=key,
                                              variant_value__iexact=value)
                product_variants.append(variant)
            except:
                pass
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variant = item.variants.all()
            ex_var_list.append(list(existing_variant))
            id.append(item.id)
        if product_variants in ex_var_list:
            index = ex_var_list.index(product_variants)
            item_id = id[index]
            cart_item = CartItem.objects.get(product=product, id=item_id)
            cart_item.quantity += 1
        elif product_variants:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            cart_item.variants.clear()
            cart_item.variants.add(*product_variants)
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if product_variants:
            cart_item.variants.clear()
            cart_item.variants.add(*product_variants)
        cart_item.save()
    return redirect('cart')


def remove_from_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, sub_total=0, tax=0, quantity=0, cart_items=None):
    color = request.GET.get('color')
    size = request.GET.get('size')
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
