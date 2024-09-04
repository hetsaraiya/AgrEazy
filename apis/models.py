from typing import Any, Iterable
from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin  

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone_number, user_type, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not phone_number:
            raise ValueError('The Phone Number field must be set')

        # Set default values for fields if not provided
        email = extra_fields.get('email', None)
        user = self.model(
            username=username,
            phone_number=phone_number,
            user_type=user_type,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, user_type='admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Ensuring superuser is active

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, phone_number, user_type, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):  # Inherit from PermissionsMixin
    FARMER = 'farmer'
    CONSUMER = 'consumer'
    ADMIN = 'admin'
    
    USER_TYPE_CHOICES = [
        (FARMER, 'Farmer'),
        (CONSUMER, 'Consumer'),
        (ADMIN, 'Admin'),
    ]
    
    username = models.CharField(max_length=100, default="", unique=True)
    phone_number = PhoneNumberField(blank=False, unique=True, null=False)
    email = models.EmailField(unique=True, blank=True, null=True)  # Optional
    password = models.CharField(max_length=100, default="")
    name = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=CONSUMER)
    
    # Add the necessary fields for Django admin and superuser functionality
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # To manage active status

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'user_type']  # You can add 'email' if you want it to be required

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    
class Product(models.Model):
    PRODUCT_CHOICES = [
        ('Product1', 'Product1'),
        ('Product2', 'Product2'),
        ('Product3', 'Product3'),
    ]
    
    name = models.CharField(max_length=100, choices=PRODUCT_CHOICES, default='Product1')
    description = models.TextField()
    price = models.FloatField()
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remaining_quantity = models.IntegerField()
    unlist = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_quantity = self.quantity
        
        try:
            if self.user.user_type != User.FARMER:
                raise ValidationError("The user must be a farmer.")
            if self.quantity < 0:
                raise ValidationError("The quantity must be greater than or equal to 0.")
            if self.remaining_quantity < 0:
                raise ValidationError("The remaining quantity must be greater than or equal to 0.")
            if self.unlist and (self.remaining_quantity > 0):
                raise ValidationError("The product cannot be unlisted if there is remaining quantity.")
            
            super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Error saving Product: {e}")
            raise

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = CloudinaryField('image')
    
    def __str__(self):
        return self.product.name

class Contract(models.Model):
    farmer = models.ForeignKey("User", on_delete=models.CASCADE, related_name='farmer_contracts')
    consumer = models.ForeignKey("User", on_delete=models.CASCADE, related_name='consumer_contracts')
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, default="CASH")
    accepted = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        try:
            if self.farmer.user_type != User.FARMER:
                raise ValidationError("The farmer must be a user with the 'farmer' user type.")
            if self.consumer.user_type != User.CONSUMER:
                raise ValidationError("The consumer must be a user with the 'consumer' user type.")
            if self.product.remaining_quantity < self.quantity:
                raise ValidationError("The product remaining quantity is less than the contract quantity.")
            
            self.product.remaining_quantity -= self.quantity
            if self.product.remaining_quantity == 0:
                self.product.unlist = True
            self.product.save()
            
            super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Error saving Contract: {e}")
            raise

    def delete(self, *args, **kwargs):
        self.product.remaining_quantity += self.quantity
        if self.product.unlist and self.product.remaining_quantity > 0:
            self.product.unlist = False
        self.product.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Contract between {self.farmer.name} and {self.consumer.name} for {self.quantity} of {self.product.name}"

def get_first_user_or_unknown():
    return User.objects.first().name if User.objects.exists() else "Unknown User"

def generate_addhar_public_id(instance):
    return f"addhar/{instance.user.name}_addhar"

def generate_pan_public_id(instance):
    return f"pan/{instance.user.name}_pan_card"

class FarmerVerificationDocs(models.Model):
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    addhar_card = models.FileField(upload_to='addhar/', blank=True, null=True)
    pan_card = models.FileField(upload_to='pan-card/', blank=True, null=True)
    satbaarcopy = models.FileField(upload_to='satbaarcopy/', blank=True, null=True)

    def __str__(self):
        # Check if user is not None, otherwise use 'Unknown User'
        user_display = self.user.username if self.user else 'Unknown User'
        return f"Verification Docs From {user_display}"

class ConsumerVerificationDocs(models.Model):
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    addhar_card = models.FileField(upload_to='addhar/', blank=True, null=True)
    pan_card = models.FileField(upload_to='pan-card/', blank=True, null=True)

    def __str__(self):
        # Check if user is not None, otherwise use 'Unknown User'
        user_display = self.user.username if self.user else 'Unknown User'
        return f"Verification Docs From {user_display}"
