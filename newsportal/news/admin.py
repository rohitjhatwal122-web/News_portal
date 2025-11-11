from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    NewsTable,
    NewsImageTable,
    SubscriptionPlans,
    SubscriptionTable,
    UserProfile,
    
)

# -------------------- 📌 Subscription Admin --------------------
@admin.register(SubscriptionTable)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan', 'amount_paid', 'payment_method', 'payment_status', 'status', 'enrolled_at']
    list_filter = ['status', 'payment_status', 'payment_method']
    search_fields = ['user__username', 'plan__name']
    actions = ['approve_payment', 'reject_payment']

    @admin.action(description="✅ Approve selected payments")
    def approve_payment(self, request, queryset):
        count = 0
        for sub in queryset:
            if sub.payment_status != 'paid':
                sub.payment_status = 'paid'
                sub.status = 'active'
                sub.payment_date = timezone.now()
                sub.expired_at = sub.enrolled_at + timezone.timedelta(days=sub.plan.days)
                sub.save()
                count += 1
        self.message_user(request, f"{count} subscription(s) approved and activated ✅")

    @admin.action(description="❌ Reject selected payments")
    def reject_payment(self, request, queryset):
        count = queryset.update(status='cancelled', payment_status='failed')
        self.message_user(request, f"{count} subscription(s) rejected ❌")

# -------------------- 📌 News Admin --------------------


@admin.register(NewsTable)
class NewsTableAdmin(admin.ModelAdmin):
    list_display = ('heading', 'category', 'published_at', 'is_featured', 'is_deleted')
    list_filter = ('category', 'is_featured', 'is_deleted')
    search_fields = ('heading', 'description')

@admin.register(NewsImageTable)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'news', 'uploaded_at')

# -------------------- 📌 Subscription Plans Admin --------------------
@admin.register(SubscriptionPlans)
class SubscriptionPlansAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

# -------------------- 📌 Custom User Admin --------------------
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, obj):
        return obj.userprofile.role if hasattr(obj, 'userprofile') else '-'
    get_role.short_description = 'Role'

# Unregister default user admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
