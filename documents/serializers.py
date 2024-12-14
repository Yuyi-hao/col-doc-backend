from rest_framework import serializers
from .models import Document, Permission
from accounts.models import User
class PublicDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'content', 'cover_image', 'created_at', 'modified_at']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class MarkPublicPrivateSerializer(serializers.Serializer):
    PERMISSION_CHOICES = ("public", "private")
    permission = serializers.ChoiceField(choices=PERMISSION_CHOICES, required=True)

class RemovePersonSerializer(serializers.Serializer): # TODO: need to validate data yet
    ACTION_CHOICES = ['request', 'change_role', 'delete']
    PERMISSION_CHOICES = ['viewer', 'editor']
    email = serializers.EmailField()
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    role = serializers.ChoiceField(choices=PERMISSION_CHOICES, required=False)

    def validate(self, attrs):
        if not User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError("This email is not attached to any user")
        if attrs.get('action') != 'delete' and attrs.get('role', None):
            raise serializers.ValidationError("The 'role' field required when updating or requesting for permission")
        return attrs
        

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields= "__all__"

class EditDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'content', 'cover_image']
        extra_kwargs = {
            'title': {'required': False},
            'content': {'required': False},
            'cover_image': {'required': False},
        }
    
    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


