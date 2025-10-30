from django.contrib import admin



from .models import *
admin.site.register(NewsTable)
admin.site.register(NewsImageTable)
admin.site.register(SubscriptionPlans)
admin.site.register(SubscriptionTable)


