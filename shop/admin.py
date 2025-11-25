from django.contrib import admin
from .models import Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'line_total')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','total_amount','status','stripe_session_id','created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('stripe_session_id',)

admin.site.register(Product)
