from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
class UserModelAdmin(BaseUserAdmin):
    list_display =  ["email", "password", "created_at", "modified_at", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ('user_credentials', {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name", "nickname", "profile_pic", "date_of_birth", "description", "location", "is_active"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "is_admin", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email", "name"]
    ordering = ["email", "id"]
    filter_horizontal = []



admin.site.register(User, UserModelAdmin)