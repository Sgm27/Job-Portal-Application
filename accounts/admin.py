from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('User Profile', {'fields': ('user_type', 'profile_picture', 'phone_number')}),
        ('Job Seeker Info', {'fields': ('resume', 'skills')}),
        ('Employer Info', {'fields': ('company_name', 'company_description', 'company_website')}),
    )

admin.site.register(User, CustomUserAdmin)
