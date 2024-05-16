from cart.views import _cart_id
from .models import Cart,CartItem


def Counter(req):   
    cart_count=0
    if 'admin' in req.path:
        return {}
    else:
        try:
            cart=Cart.objects.filter(cart_id =_cart_id(req))
            if req.user.is_authenticated:
                cart_item = CartItem.objects.all().filter(user=req.user)
            else:
                cart_item = CartItem.objects.all().filter(cart=cart[:1])
            for item in cart_item:
                cart_count += item.quantity
        except:
            cart_count=0
    return dict(cart_count=cart_count)