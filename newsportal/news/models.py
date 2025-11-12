from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# -------------------- CATEGORY MODEL --------------------
# class NewsCategory(models.Model):

CATEGORY_CHOICES = (
        ('Latest News', 'Latest News'),
        ('News', 'News'),
        ('India News', 'India News'),
        ('World News', 'World News'),
        ('Local News', 'Local News'),
        ('Sports News', 'Sports News'),
        ('Film Industry News', 'Film Industry News'),
        ('Political News', 'Political News'),
        ('Crime News', 'Crime News'),
        ('Accounts News', 'Accounts News'),
        ('Market News', 'Market News'),
        ('Health and Wellness', 'Health and Wellness'),
        ('Technology and Science', 'Technology and Science'),
        ('Business and Finance', 'Business and Finance'),
    )
    # name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    # def __str__(self):
    #     return self.name


# -------------------- NEWS MODEL --------------------
class NewsTable(models.Model):
    heading = models.CharField(max_length=255)
    heading_image = models.ImageField(upload_to='news_images/')
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    description_2 = models.TextField()
    # category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES , default='Latest News')
    is_featured = models.BooleanField(default=False)

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


# -------------------- NEWS IMAGE MODEL --------------------
class NewsImageTable(models.Model):
    news = models.ForeignKey(NewsTable, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news_images/multiple/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
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


# -------------------- SUBSCRIPTION PLANS --------------------
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


# -------------------- SUBSCRIPTION TABLE --------------------
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
    plan = models.ForeignKey(SubscriptionPlans, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField()
    renew_at = models.DateTimeField(null=True, blank=True)
    renew_end_at = models.DateTimeField(null=True, blank=True)
    is_trial = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

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


# -------------------- USER PROFILE --------------------
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('Editor', 'Editor'),
        ('Journalist', 'Journalist'),
        ('User', 'User'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ============================== NEWS VIDEO MODEL ==============================

from django.db import models

class NewsVideo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
