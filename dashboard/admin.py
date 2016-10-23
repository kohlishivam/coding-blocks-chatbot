from django.contrib import admin


# Register your models here.
from dashboard.models import Messages, UserProfile

admin.site.register(Messages)
admin.site.register(UserProfile)
