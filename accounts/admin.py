from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "email", "date_of_birth", "tc", "name", "is_admin", "created_at", "updated_at"]
    list_filter = ["is_admin"]
    fieldsets = [
        ('user_credentials', {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name", "date_of_birth", "tc"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "tc", "is_admin", "date_of_birth", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email", "name"]
    ordering = ["email", "id"]
    filter_horizontal = []



admin.site.register(User, UserModelAdmin)