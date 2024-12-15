from accounts.models import User
from django.db import transaction, IntegrityError
from .models import Document, Permission, DocumentRequest
from notifications.models import Notification
from django.core.exceptions import ObjectDoesNotExist
from core.utils import response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from . import serializers
# Create your views here.

@api_view(['GET'])
def read_public_doc(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, is_public=True)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    return response(
        message="Document Fetched successfully",
        success=True,
        status_code=status.HTTP_200_OK,
        content={
            'document': serializers.PublicDocumentSerializer(document).data
        }
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_documents(request):
    try:
        document_owned = Document.objects.filter(owner=request.user)
        document_shared = Document.objects.filter(permission__user=request.user).select_related('permission')
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
            'document_owned':  serializers.DocumentSerializer(document_owned, many=True).data,
            'document_shared': serializers.SharedDocumentSerializer(document_shared, many=True).data
        }
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def create_doc(request):
    try:
        document = Document.objects.create(owner=request.user)
    except Exception as e:
        return response(
            success=False,
            message="Failed to create document.",
            code="document-creation-failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response(
        message="Document Fetched successfully",
        success=True,
        status_code=status.HTTP_201_CREATED,
        content={
            'document': serializers.DocumentSerializer(document).data
        }
    )

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated,])
def edit_doc(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    # permission check 
    if document.owner == request.user or Permission.objects.filter(document=document, user=request.user, role='editor').exists():
        serialize = serializers.EditDocumentSerializer(instance=document, data=request.data, partial=True)
        if not serialize.is_valid():
            return response(
                success = False,
                message = "Incorrect data",
                code = "invalid-data",
                status_code = status.HTTP_400_BAD_REQUEST,
            )
        serialize.save()
        return response(
            message="Document Updated successfully",
            success=True,
            status_code=status.HTTP_200_OK,
            content={
                'document': serializers.DocumentSerializer(document).data
            }
        )
    else:
        return response(
            success = False,
            message = "You don't have permission to modified this documents",
            code = "no-permission",
            status_code = status.HTTP_403_FORBIDDEN,
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def view_doc(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    if document.owner == request.user or Permission.objects.filter(document=document.id, user=request.user).exists():
        serialize_data = serializers.DocumentSerializer(document).data
    elif document.is_public:
        serialize_data = serializers.PublicDocumentSerializer(document).data
    else:
        return response(
            success = False,
            message = "You don't have permission to view this document.",
            code = "permission-denied",
            status_code = status.HTTP_403_FORBIDDEN,
        )
    return response(
        message="Document Updated successfully",
        success=True,
        status_code=status.HTTP_200_OK,
        content={
            'document': serialize_data
        }
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,])
def delete_doc(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, owner=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist or you don't have permission to perform this operation",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    document.delete()
    return response(
        success=True,
        code='document-deleted-successfully',
        status_code=status.HTTP_204_NO_CONTENT
    )

# TODO: as it requires request app
@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def doc_share_request_reply(request, request_slug):
    try:
        document_request = DocumentRequest.objects.get(slug=request_slug, recipient=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Request doesn't exist.",
            code = "request-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    if document_request.response:
        return response(
            success = False,
            message = "You have already responded to this request",
            code = "request-already-responded",
            status_code = status.HTTP_400_BAD_REQUEST,
        )
    serialize = serializers.DocumentRequestResponseSerializer(data=request.data)
    if not serialize.is_valid():
        return response(
            success = False,
            message = "Incorrect data.",
            code = "invalid-data",
            status_code = status.HTTP_400_BAD_REQUEST,
        )
    data = request.data.get('response')
    try:
        with transaction.atomic():  # Ensure atomicity
            if data == 'accepted':
                # Create permission
                Permission.objects.create(
                    document=document_request.document,
                    user=document_request.sender,
                    role=document_request.role
                )
                document_request.response = 'accepted'
            elif data == 'declined':
                document_request.response = 'declined'
            Notification.objects.create(
                recipient=document_request.sender,
                sender=document_request.recipient,
                notification_text=f"{document_request.recipient} {data} your request for {document_request.document}."

            )
            content = {
                'request': serializers.RequestSerializer(document_request).data
            }
            document_request.save()
    except Exception as e:
        return response(
            success=False,
            message="An error occurred while processing the request.",
            code="request-processing-error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)},
        )

    return response(
        message=f"Request {data} successfully.",
        success=True,
        status_code=status.HTTP_200_OK,
        content=content
    )

# TODO: need to do it 
@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def modify_document_permission (request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, owner=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    
    serialize = serializers.RemovePersonSerializer(data=request.data)
    if not serialize.is_valid():
        return response(
            success = False,
            message = "Incorrect data",
            code = "invalid-data",
            status_code = status.HTTP_400_BAD_REQUEST,
        )

    email = request.data.get('email')
    action = request.data.get('action')
    if action == 'request':
        role = request.data.get('role')
        try:
            with transaction.atomic():
                share_request = DocumentRequest.objects.create(
                    recipient=User.objects.get(email=email),
                    sender=request.user,
                    document=document,
                    role=role
                )
                Notification.objects.create(
                    recipient=User.objects.get(email=email),
                    sender=request.user,
                    notification_text=f"{request.user} requested you for {document} as {role}."

                )
        except IntegrityError:
            return response(
                success = False,
                message = "Failed to create request",
                code = "request-failed",
                status_code = status.HTTP_404_NOT_FOUND,
            )

        return response(
            success = True,
            message = "Request has been sent to the user",
            code = "request-sent",
            status_code = status.HTTP_201_CREATED,
            content={
                'request' : serializers.RequestSerializer(share_request).data,
            }
        )

    try:
        permission = Permission.objects.get(document=document.id, user__email=email)
    except Permission.DoesNotExist:
        return response(
            success = False,
            message = "This user has no permission on this document",
            code = "permission-not-found",
            status_code = status.HTTP_404_NOT_FOUND,
        )

    if action == 'change_role':
        role = request.data.get('role')
        if permission.role == role:
            return response(
                message="User already have same role",
                success=False,
                code='no-change-in-role',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        permission.role = role
        permission.save()
        return response(
            message="Permission updated successfully",
            success=True,
            status_code=status.HTTP_200_OK,
        )
    elif action == 'delete':
        permission.delete()
        return response(
            message="Permission deleted successfully",
            success=True,
            status_code=status.HTTP_204_NO_CONTENT,
        )

    return response(
        success=False,
        message="Incorrect data",
        code="invalid-data",
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def mark_doc_public_or_private(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, owner=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist or you don't have permission to perform this operation.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    serialize = serializers.MarkPublicPrivateSerializer(data=request.data)
    if not serialize.is_valid():
        return response(
            success = False,
            message = "Incorrect data",
            code = "invalid-data",
            status_code = status.HTTP_400_BAD_REQUEST,
        )
    permission = request.data.get('permission')
    if (permission == 'public' and document.is_public) or (permission == 'private' and document.is_public == False):
        return response(
            success=False,
            message="The document is already in the requested visibility state.",
            code="no-change-required",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if permission == 'public':
        document.is_public = True
    elif permission == 'private':
        document.is_public = False
    document.save()
    return response(
        message="Document visibility updated successfully.",
        success=True,
        status_code=status.HTTP_200_OK,
        content={
            'document': serializers.DocumentSerializer(document).data
        }
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def get_share_list(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, owner=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist or you don't have permission to perform this operation.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    if document.is_public:
        return response(
            message="This document is public and accessible to everyone.",
            status="document-is-public",
            code='public-document',
            status_code=status.HTTP_200_OK,
        )
    shared_list = Permission.objects.filter(document=document)

    return response(
        message='list fetched successfully',
        status="list-fetch-successfully",
        status_code=status.HTTP_200_OK,
        content={
            'shared_list': serializers.PermissionSerializer(shared_list, many=True).data
        }
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def list_requests(request):
    all_requests_sent = DocumentRequest.objects.filter(sender=request.user)
    all_requests_receive = DocumentRequest.objects.filter(recipient=request.user)
    return response(
        message='Requests fetched successfully',
        status="request-fetch-successfully",
        status_code=status.HTTP_200_OK,
        content={
            'all_requests_sent': serializers.RequestSerializer(data=all_requests_sent, many=True).data,
            'all_requests_receive': serializers.RequestSerializer(data=all_requests_receive, many=True).data,
        }
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, ])
def delete_requests(request, request_slug):
    try:
        document_request = DocumentRequest.objects.get(slug=request_slug, sender=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Request doesn't exist or you don't have permission to perform this operation",
            code = "request-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    document_request.delete()
    return response(
        success=True,
        code='request-deleted-successfully',
        status_code=status.HTTP_204_NO_CONTENT
    )