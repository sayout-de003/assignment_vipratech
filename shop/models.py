# shop/models.py
from django.db import models
from django.conf import settings

class Product(models.Model):
    name = models.CharField(max_length=120)
    price = models.PositiveIntegerField(help_text='Amount in smallest currency unit e.g., paise (₹)')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.PositiveIntegerField(default=0)  # in paise
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.pk} - {self.status}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    line_total = models.PositiveIntegerField(help_text='Amount in paise')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
