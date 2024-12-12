from django.db import models
from accounts.models import User

# Create your models here.
class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_documents')
    title = models.CharField(max_length=100, blank=False, null=False, default='untitled')
    content = models.TextField()
    shared_with = models.ManyToManyField(User, related_name='shared_documents', null=True, blank=True)
    is_public_view = models.BooleanField(default=False)
    is_public_edit = models.BooleanField(default=False)
    
    # auto field
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)
    
    def __str__(self) -> str:
        return self.title