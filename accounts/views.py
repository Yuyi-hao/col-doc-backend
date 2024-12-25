from core.utils import response, get_tokens_for_user
from django.utils import timezone
from rest_framework import status
from .models import User
from rest_framework.decorators import api_view, permission_classes
from .serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLogoutSerializer, UserPasswordResetSerializer, UserRegisterSerializer, UserSerializer, UserLoginSerializer, UserUpdateSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from core.utils import send_email
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def register_user(request):
    serialize = UserRegisterSerializer(data=request.data)
    if not serialize.is_valid(raise_exception=True):
        try:
            message = ' or '.join(str(i[0]) for i in serialize.errors.values())
        except:
            message = "Incomplete data"
        return response(
            message=message,
            success=False,
            code="input-required", 
            error=serialize.errors,
            status_code = status.HTTP_400_BAD_REQUEST
        )
    data = serialize.validated_data
    data['email'] = data.get('email').lower()
    try:
        if User.objects.filter(email=data.get('email')).exists():
            return response(
                success = False,
                message = "Email already exist",
                code = "email-exist",
                status_code = status.HTTP_400_BAD_REQUEST,
            )
        user = serialize.save()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        refresh_token, access_token  = get_tokens_for_user(user)
        send_response =   response(
            message="Registration successful",
            success=True,
            status_code=status.HTTP_201_CREATED,
            content={
                'user': UserSerializer(user).data,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )
        send_response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        return send_response
    except Exception as e:
        return response(
            success = False,
            message = f"something went wrong. {[e]}",
            code = "internal-server-error",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['POST'])
def login_user(request):
    serialize = UserLoginSerializer(data=request.data)
    if not serialize.is_valid(raise_exception=True):
        try:
            message = ' or '.join(str(i[0]) for i in serialize.errors.values())
        except:
            message = "Incomplete data"
        return response(
            message=message,
            success=False,
            code="input-required", 
            error=serialize.errors,
            status_code = status.HTTP_400_BAD_REQUEST
        )
    data = serialize.validated_data
    data['email'] = data.get('email').lower()
    try:
        if not User.objects.filter(email=data.get('email')).exists():
            return response(
                success = False,
                message = "Email address doesn't exist.",
                code = "email-not-exist",
                status_code = status.HTTP_404_NOT_FOUND,
            )
        user = authenticate(email=data.get('email'), password=data.get('password'))
        if not user:
            return response(
                success = False,
                message = "email or password doesn't match",
                code = "incorrect-inputs",
                status_code = status.HTTP_400_BAD_REQUEST,
            )

        refresh_token, access_token  = get_tokens_for_user(user)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        send_response =  response(
            message="Login successful",
            success=True,
            status_code=status.HTTP_200_OK,
            content={
                'user': UserSerializer(user).data,
                'access_token': access_token,
                'refresh_token': refresh_token
            },
        )
        send_response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        return send_response
    except Exception as e:
        return response(
            success = False,
            message = f"something went wrong. {[e]}",
            code = "internal-server-error",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated,])
def profile_user(request):
    user = request.user
    if request.method == 'GET':
        return response(
            message='user-fetched-successfully',
            success=True,
            status_code=status.HTTP_200_OK,
            content={
                'user': UserSerializer(request.user).data,
            }
        )
    elif request.method == "PUT":
        if not request.data:
            return response(
                message='invalid data',
                code='empty-data',
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        fields = list(request.data.keys())
        for field in fields:
            print(getattr(user, field))
            if hasattr(user, field) and getattr(user, field) == request.data[field]:
                request.data.pop(field)
        
        print(request.data)

        if not request.data:
            return response(
                message='No data has been changed',
                code="invalid-data",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        serialize = UserUpdateSerializer(data=request.data)
        serialize.is_valid(raise_exception=True)
        serialize.update(user, request.data)
        
        return response(
            message='user-updated-successfully',
            success=True,
            status_code=status.HTTP_200_OK,
            content={
                'user': UserSerializer(user).data,
            }
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def logout_user(request):
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        access_token = request._authenticator.get_header(request).decode('utf-8').split()[1]
    except Exception as e:
        return response(
            success = False,
            message = f"something went wrong. {[e]}",
            code = "internal-server-error",
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        )    
    serialize = UserLogoutSerializer(data=request.data, context={'refresh_token': refresh_token, 'access_token': access_token })
    if serialize.is_valid(raise_exception=True):
        return response(
            message='user-logged-out-successfully',
            success=True,
            status_code=status.HTTP_205_RESET_CONTENT,
        )
    else:
        return response(
            success = False,
            message = f"Invalid or Expired Token",
            code = "invalid-tokens",
            status_code = status.HTTP_400_BAD_REQUEST,
        )    


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def change_password_user(request):
    serialize = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
    if not serialize.is_valid(raise_exception=True):
        try:
            message = ' or '.join(str(i[0]) for i in serialize.errors.values())
        except:
            message = "Incomplete data"
        return response(
            message=message,
            success=False,
            code="input-required", 
            error=serialize.errors,
            status_code = status.HTTP_400_BAD_REQUEST
        )
    return response(
        message="Your password successfully changed.",
        success=True,
        code="password-change-successfully", 
        status_code = status.HTTP_200_OK
    )  

# FIXME: Need to fix gmail issue
@api_view(['POST'])
def send_password_reset_email_user(request):
    return response(
        message="NOT IMPLEMENTED",
        success=False,
        code="under-development",
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    )
    serialize = SendPasswordResetEmailSerializer(data=request.data)
    if not serialize.is_valid(raise_exception=True):
        try:
            message = ' or '.join(str(i[0]) for i in serialize.errors.values())
        except:
            message = "Incomplete data"
        return response(
            message=message,
            success=False,
            code="input-required", 
            error=serialize.errors,
            status_code = status.HTTP_400_BAD_REQUEST
        )
    return response(
        message="email sent successfully to change your password.",
        success=True,
        code="email-sent-successfully", 
        status_code = status.HTTP_200_OK
    )

# FIXME: Need to fix the issue but ig it works
@api_view(["POST"])
def password_reset_user(request, uid, token):
    return response(
        message="NOT IMPLEMENTED",
        success=False,
        code="under-development",
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    )
    serialize = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
    if not serialize.is_valid(raise_exception=True):
        try:
            message = ' or '.join(str(i[0]) for i in serialize.errors.values())
        except:
            message = "Incomplete data"
        return response(
            message=message,
            success=False,
            code="input-required", 
            error=serialize.errors,
            status_code = status.HTTP_400_BAD_REQUEST
        )
    return response(
        message="Your password successfully changed.",
        success=True,
        code="password-change-successfully", 
        status_code = status.HTTP_200_OK
    )


@api_view(["POST"])
def access_from_refresh(request):
    refresh_token = request.data.get('refresh_token')
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
    except Exception as e:
        return response(
            message='Invalid token',
            code='refresh-token-invalid',
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False
        )
    
    return response(
        message='access token',
        code='access-token',
        status_code=status.HTTP_200_OK,
        content={
            'access_token': access_token
        }
    )