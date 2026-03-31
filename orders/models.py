from django.conf import settings
from django.db import models
from django.utils import timezone


class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seller_code = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.display_name} ({self.seller_code})"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('COD', 'COD'),
        ('PREPAID', 'Prepaid'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('RTO', 'RTO'),
        ('CANCELLED', 'Cancelled'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=40, unique=True, blank=True)
    customer_name = models.CharField(max_length=150)
    full_address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20)
    product = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tag = models.CharField(max_length=120, blank=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            date_part = timezone.localdate().strftime('%Y%m%d')
            prefix = self.seller.seller_code.upper()
            payment_part = 'COD' if self.payment_type == 'COD' else 'PRE'
            count_today = Order.objects.filter(
                seller=self.seller,
                order_date=self.order_date,
                payment_type=self.payment_type,
            ).count() + 1
            self.order_id = f"{prefix}{payment_part}{date_part}{count_today:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.customer_name}"
