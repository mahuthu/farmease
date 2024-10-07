from django.db import models
from django.contrib.auth.models import User

# Create your models here.

    

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('processor', 'Processor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True)  # Role will be set after login
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    account_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Processor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=50)
    license_no = models.CharField(max_length=50)
    certification = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # services = models.ManyToManyField('processing.Service', related_name='processors')  # Processors can offer multiple services
    # products = models.ManyToManyField('processing.Product', blank=True, related_name='processors')
    # price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    # min_amount = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.business_name