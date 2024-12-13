from rest_framework import serializers
from .models import Document, Permission

class DocumentSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField()
    class Meta:
        model = Document
        fields = "__all__"

class MarkPublicPrivateSerializer(serializers.Serializer):
    PERMISSION_CHOICES = ("public", "private")
    permission = serializers.ChoiceField(choices=PERMISSION_CHOICES)

class RemovePersonSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields= "__all__"



