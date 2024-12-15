from django.db import models
from accounts.models import User
import uuid

# Create your models here.
class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_documents')
    title = models.CharField(max_length=100, blank=False, null=False, default='untitled')
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    slug = models.UUIDField(default=uuid.uuid4)

    # Additional 
    cover_image = models.CharField(max_length=255, blank=True, null=True)

    # auto field
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)
    
    def __str__(self) -> str:
        return self.title
    
class Permission(models.Model):
    PERMISSION_CHOICES = [
        ('Viewer', 'viewer'),
        ('Editor', 'editor'),
    ]
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='permission_document')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=PERMISSION_CHOICES)

    # auto field
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    class Meta:
        unique_together = ('document', 'user')


class DocumentRequest(models.Model):
    RESPONSE_CHOICES = [
        ('declined', 'declined'),
        ('accepted', 'accepted')
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_sender')
    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_recipient')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='requested_document')
    role = models.CharField(max_length=50, choices=Permission.PERMISSION_CHOICES)
    slug = models.UUIDField(uuid.uuid4)

    # response fields
    response = models.CharField(max_length=50, choices=RESPONSE_CHOICES, null=True, blank=True)

    # auto field
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    class Meta:
        unique_together = ('sender', 'document', 'role')