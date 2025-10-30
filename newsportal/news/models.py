from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class NewsTable(models.Model):
    heading = models.CharField(max_length=255)
    heading_image = models.ImageField(upload_to='news_images/')
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    description_2 = models.TextField()

    # Soft Delete Fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return self.heading


class NewsImageTable(models.Model):
    news = models.ForeignKey(NewsTable, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news_images/multiple/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Soft Delete Fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def __str__(self):
        return f"Image for {self.news.heading}"


class SubscriptionPlans(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    days = models.IntegerField()
    features = models.TextField()

    is_trial_available = models.BooleanField(default=False)
    trial_days = models.IntegerField(default=0)

    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    max_devices = models.IntegerField(default=1)
    priority_support = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models


class SubscriptionTable(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey('SubscriptionPlans', on_delete=models.CASCADE)

    enrolled_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField()

    renew_at = models.DateTimeField(null=True, blank=True)
    renew_end_at = models.DateTimeField(null=True, blank=True)

    is_trial = models.BooleanField(default=False)

    auto_renew = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # ✅ Payment fields added
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_active(self):
        return self.status == 'active'
