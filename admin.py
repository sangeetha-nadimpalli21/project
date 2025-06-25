from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Lead, CallLog

admin.site.register(Lead)
admin.site.register(CallLog)
