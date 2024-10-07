from django.contrib import admin
from .models import User, UserProfile, Farmer, Processor



class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username',)

class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username',)

class ProcessorAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'contact_number')
    search_fields = ('user__username', 'business_name')

# Register your models here with custom admin classes.

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Farmer, FarmerAdmin)
admin.site.register(Processor, ProcessorAdmin)