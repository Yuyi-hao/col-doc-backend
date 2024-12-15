from django.db import models
from accounts.models import User
# Create your models here.
class Notification(models.Model):
    # user fields
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="notification owner")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="notification sender")

    notification_text = models.CharField(max_length=500, null=False, blank=False)

    # auto field
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)