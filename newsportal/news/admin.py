# from django.contrib import admin



# from .models import *
# admin.site.register(NewsTable)
# admin.site.register(NewsImageTable)
# admin.site.register(SubscriptionPlans)
# admin.site.register(SubscriptionTable)

from django.contrib import admin
from django.utils import timezone
from .models import NewsTable, NewsImageTable, SubscriptionPlans, SubscriptionTable

# Register News and Image
admin.site.register(NewsTable)
admin.site.register(NewsImageTable)
admin.site.register(SubscriptionPlans)

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
