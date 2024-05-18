from django.shortcuts import get_object_or_404, redirect, render

from cart.models import CartItem
from orders.models import OrderProduct
from store.forms import ReviewForm
from django.contrib import messages
from .models import Product,Category, Review
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
    if req.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=req.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = Review.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    #product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        #'product_gallery':product_gallery,
        }

    return render(req,'product_detail.html',context)

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

def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER') #store previous url
    if request.method == 'POST':
        try:
            reviews = Review.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except Review.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = Review()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)