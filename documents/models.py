from django.db import models
from accounts.models import User

# Create your models here.
class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_documents')
    title = models.CharField(max_length=100, blank=False, null=False, default='untitled')
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    slug = models.SlugField(verbose_name="document slug")
    # TODO: group edit and view
    # is_group_view = models.BooleanField(default=None)
    # is_group_edit = models.BooleanField(default=False)

    # Additional 
    cover_image = models.TextField()
    word_count = models.IntegerField()
    character_count = models.IntegerField()
    reading_time = models.TimeField()

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
    permission = models.CharField(max_length=50, choice=PERMISSION_CHOICES)

