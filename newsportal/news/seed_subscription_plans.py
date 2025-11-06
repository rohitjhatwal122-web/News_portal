from django.utils.text import slugify
from .models import SubscriptionPlans

def run():
    plans_data = [
        {
            "name": "Basic",
            "price": 99.00,
            "days": 30,
            "features": "Access to basic content, 1 device, Email support",
            "is_trial_available": True,
            "trial_days": 7,
            "discount_price": 79.00,
            "max_devices": 1,
            "priority_support": False,
        },
        {
            "name": "Premium",
            "price": 199.00,
            "days": 90,
            "features": "Access to premium content, up to 3 devices, Priority email support",
            "is_trial_available": True,
            "trial_days": 14,
            "discount_price": 159.00,
            "max_devices": 3,
            "priority_support": True,
        },
        {
            "name": "Advanced",
            "price": 499.00,
            "days": 365,
            "features": "All content access, up to 5 devices, 24/7 priority support",
            "is_trial_available": False,
            "trial_days": 0,
            "discount_price": 399.00,
            "max_devices": 5,
            "priority_support": True,
        },
    ]

    for plan in plans_data:
        obj, created = SubscriptionPlans.objects.get_or_create(
            slug=slugify(plan["name"]),
            defaults=plan
        )
        if created:
            print(f"✅ Created: {plan['name']}")
        else:
            print(f"⚠️ Already exists: {plan['name']}")
