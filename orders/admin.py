from django.contrib import admin

from orders.models import Order, OrderProduct, Payment

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','email','pin_code','order_total','status','is_ordered','created_at']

    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','email']
    list_per_page = 15
    inlines = [OrderProductInline]
    
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)