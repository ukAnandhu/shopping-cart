from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from cart.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variation
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(req):
    cart = req.session.session_key
    if not cart:
        cart = req.session.create()

    return cart

def add_cart(req,product_id):
    #product
    current_user = req.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
        if req.method == 'POST':
            for item in req.POST:
                key = item
                value = req.POST[key]
                
                #variation
                try:
                    variation  =Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        is_cart_item_exists = CartItem.objects.filter(product=product,user = current_user).exists()
        #cart_item
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                #quantity increase
                index = ex_var_list.index(product_variation)
                item_id= id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()
            else: 
                item = CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    else:
        product_variation = []
        if req.method == 'POST':
            for item in req.POST:
                key = item
                value = req.POST[key]
                
                #variation
                try:
                    variation  =Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        #cart
        try:
            cart = Cart.objects.get(cart_id=_cart_id(req)) #get the cart using the cart id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(req)
            )
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        #cart_item
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)
            if product_variation in ex_var_list:
                #quantity increase
                index = ex_var_list.index(product_variation)
                item_id= id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()
            else: 
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                cart=cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

def remove_cart(req,product_id,item_id):
        product = get_object_or_404(Product,id=product_id)
        try:
            if req.user.is_authenticated:
                cart_item = CartItem.objects.get(product=product,user=req.user,id=item_id)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(req))
                cart_item = CartItem.objects.get(product=product,cart=cart,id=item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass 
        return redirect('cart')

def remove_cart_item(req,product_id,item_id):
    product = get_object_or_404(Product,id=product_id)
    if req.user.is_authenticated:
                cart_item = CartItem.objects.get(product=product,user=req.user,id=item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(req))
        cart_item = CartItem.objects.get(product=product,cart=cart,id=item_id)
    cart_item.delete()
    return redirect('cart')


def cart(req,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if req.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=req.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(req))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (3 * total)/100
        grand_total = total + tax
    except :
        pass 
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total':grand_total,
        'tax':tax

    }
    return render(req,'cart.html',context)


@login_required(login_url='login')
def checkout(req,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if req.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=req.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(req))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (3 * total)/100
        grand_total = total + tax
    except:
        pass
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total':grand_total,
        'tax':tax

    }
    return render(req,'checkout.html',context)