from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def calculate_on_time_delivery_rate(self):
        total_completed_orders = self.purchase_orders.filter(status='completed').count()
        if total_completed_orders == 0:
            return 0
        on_time_delivered_orders = self.purchase_orders.filter(status='completed', delivery_date__lte=timezone.now()).count()
        return (on_time_delivered_orders / total_completed_orders) * 100

    def calculate_quality_rating_avg(self):
        completed_orders_with_ratings = self.purchase_orders.filter(status='completed', quality_rating__isnull=False)
        if completed_orders_with_ratings.exists():
            return completed_orders_with_ratings.aggregate(avg_rating=Avg('quality_rating'))['avg_rating']
        return 0

    def calculate_average_response_time(self):
        acknowledged_orders = self.purchase_orders.filter(acknowledgment_date__isnull=False)
        print("===",acknowledged_orders)
        if acknowledged_orders.exists():
            total_response_time = sum((order.acknowledgment_date - order.issue_date).seconds for order in acknowledged_orders)
            print("---",total_response_time / acknowledged_orders.count())
            return total_response_time / acknowledged_orders.count()
        return 0

    def calculate_fulfillment_rate(self):
        total_orders = self.purchase_orders.count()
        if total_orders == 0:
            return 0
        fulfilled_orders = self.purchase_orders.filter(status='completed').count()
        return (fulfilled_orders / total_orders) * 100

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    po_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    items = models.TextField()
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, default='pending')
    quality_rating = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.po_number
