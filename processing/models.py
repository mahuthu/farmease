from django.db import models

# Create your models here.


class Service(models.Model):
    # processor = models.ForeignKey('user_app.Processor', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    # quantity = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name





class ProductService(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='product_services')
    processor = models.ForeignKey('user_app.Processor', on_delete=models.CASCADE, related_name='product_services')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('product', 'service', 'processor')  # Ensure a processor can't add the same service for the same product twice

    def __str__(self):
        return f"{self.processor.business_name} - {self.service.name} for {self.product.name}"



class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    ]


    farmer = models.ForeignKey('user_app.Farmer', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    processor = models.ForeignKey("user_app.Processor", on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Updated status field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default value here
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Add total_price field

    def __str__(self):
        return f"Booking of {self.product} by {self.farmer} for {self.service}"
