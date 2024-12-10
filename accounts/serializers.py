from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from core.utils import send_email
from .models import User
from rest_framework_simplejwt.tokens import  RefreshToken

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2', 'tc', 'date_of_birth']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    password2 = serializers.CharField(style={
        'input_type': 'password'
    }, write_only=True)
    
    def create(self, validate_data):
        return User.objects.create_user(**validate_data)
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match with confirm password")
        return attrs
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'date_of_birth', 'tc']
    
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']

class UserLogoutSerializer(serializers.Serializer):
    class Meta:
        fields = []
    
    def validate(self, attrs):
        try:
            refresh_token = RefreshToken(self.context.get('refresh_token'))
            refresh_token.blacklist()
            return attrs
        except:
            raise serializers.ValidationError("Invalid Token or Token has been blacklisted")

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={
        'input_type': 'password'
    }, write_only=True)
    password2 = serializers.CharField(max_length=255, style={
        'input_type': 'password'
    }, write_only=True)
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match with confirm password")
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.get(email=email)
        if not user:
            raise serializers.ValidationError('This email address is not registered.')
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_password_endpoint = "http://127.0.0.1:8000/accounts/reset-password"
        link = f'{reset_password_endpoint}/{uid}/{token}/'
        data = {
            'subject': "Request to reset password",
            'body': f"Click following link to reset your password. {link}",
            'to_email': user.email,
        }
        # FIXME: need to fix this 
        # try:
        #     send_email(data)
        # except:
        #     raise serializers.ValidationError("Couldn't sent reset email to specified email address.")
        return attrs

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={
        'input_type': 'password'
    }, write_only=True)
    password2 = serializers.CharField(max_length=255, style={
        'input_type': 'password'
    }, write_only=True)
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password doesn't match with confirm password")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Invalid or Expired Token")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not Valid or Expired')
    
    