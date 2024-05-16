from django.shortcuts import get_object_or_404, render

from cart.models import CartItem

from .models import Product,Category
from cart.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q

# Create your views here.
def store(req,category_slug=None):
    category = None
    products = None
    if category_slug != None:
        category = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.all().filter(category=category,is_available=True)
        paginator = Paginator(products,3)
        page = req.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products,6)
        page = req.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    
    return render(req,'store.html',{'products':paged_products,'product_count':product_count})

def product_detail(req,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(req),product=single_product)
        

    except Exception as e:
        raise e
    return render(req,'product_detail.html',{'single_product':single_product,'in_cart':in_cart})

def search(req):
    if 'keyword' in req.GET:
        keyword = req.GET['keyword']
        if keyword:
            products= Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) |  Q(product_name__icontains=keyword))
            product_count =products.count()
    context = {
        'products':products,
        'product_count':product_count,
    }

    
    return render(req,'store.html',context)

