from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core.utils import response
from rest_framework import status
from .models import Notification
from django.core.exceptions import ObjectDoesNotExist
from . import serializers

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def notifications(request):
    try:
        notifications = Notification.objects.filter(recipient=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "notification doesn't exist.",
            code = "notification-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    return response(
        success = True,
        message = "notification fetched successfully",
        code = "notification-fetched-success",
        status_code = status.HTTP_200_OK,
        content={
            'notifications': serializers.NotificationSerializer(notifications, many=True).data,
            'unread_notification_count': notifications.filter(is_read=False).count()
        }
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated,])
def mark_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "notification doesn't exist.",
            code = "notification-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    notification.is_read = True
    notification.save()
    return response(
        success = True,
        message = "notification marked as read",
        code = "notification-marked-read",
        status_code = status.HTTP_200_OK,
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,])
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient =request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "notification doesn't exist.",
            code = "notification-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    notification.delete()
    return response(
        success=True,
        code='notification-deleted-successfully',
        status_code=status.HTTP_204_NO_CONTENT
    )