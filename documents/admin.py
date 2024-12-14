from django.contrib import admin
from .models import Document, Permission

# Register Document model
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'created_at', 'modified_at')
    search_fields = ('title', 'owner__email') 
    list_filter = ('is_public', 'created_at')  

admin.site.register(Document, DocumentAdmin)

# Register Permission model
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'role', 'created_at')
    search_fields = ('document__title', 'user__email')  

admin.site.register(Permission, PermissionAdmin)
