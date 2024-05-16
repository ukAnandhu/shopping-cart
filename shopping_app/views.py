from django.shortcuts import render

from store.models import Product

# Create your views here.

def demo(req):
    products = Product.objects.all().filter(is_available=True)
    
    return render(req,'index.html',{'products':products})