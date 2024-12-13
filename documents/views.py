from django.shortcuts import render
from .models import Document, Permission
from django.core.exceptions import ObjectDoesNotExist
from core.utils import response
from rest_framework import status
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
            'document': serializers.DocumentSerializer(document).data
        }
    )
    
# TODO: need to add custom data
@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def create_doc(request):
    document = Document.objects.create(owner=request.user)
    if request.data:
        pass # TODO: see how can you assign value after creating
    document.save()
    return response(
        message="Document Fetched successfully",
        success=True,
        status_code=status.HTTP_200_OK,
        content={
            'document': serializers.DocumentSerializer(document).data
        }
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def edit_doc(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, is_public=True)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    pass

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
    if document.owner == request.user or Permission.objects.get(document=document.id, user=request.user):
        return response(
            message="Document Updated successfully",
            success=True,
            status_code=status.HTTP_200_OK,
            content={
                'document': serializers.DocumentSerializer(document).data
            }
        )
    
    return response(
        success = False,
        message = "Document doesn't exist.",
        code = "document-not-exist",
        status_code = status.HTTP_404_NOT_FOUND,
    )

@api_view(['POST'])
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
        message="Document deleted successfully.",
        success=True,
        code='document-deleted-successfully',
        status_code=status.HTTP_204_NO_CONTENT
    )


# TODO: as it requires request app
@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def doc_share_request(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, is_public=True, owner=request.user)
    except ObjectDoesNotExist:
        return response(
            success = False,
            message = "Document doesn't exist.",
            code = "document-not-exist",
            status_code = status.HTTP_404_NOT_FOUND,
        )
    if document.owner == request.user:
        pass
    elif True:
        pass


# TODO: need to do it 
@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def remove_person_from_share_list(request, document_slug):
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
    if serialize.is_valid():
        return response(
            success = False,
            message = "Incorrect data",
            code = "invalid-data",
            status_code = status.HTTP_400_BAD_REQUEST,
        )
    
    email = request.data.get('email')
    permission = Permission.objects.get(document=document.id, user__email=email)
    if not permission:
        return response(
            success = False,
            message = "Incorrect data",
            code = "invalid-data",
            status_code = status.HTTP_400_BAD_REQUEST,
        )
    permission.delete()
    return response(
        message="Document Fetched successfully",
        success=True,
        status_code=status.HTTP_200_OK,
        content={
            'document': serializers.DocumentSerializer(document).data
        }
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
    if serialize.is_valid():
        return response(
            success = False,
            message = "Incorrect data",
            code = "invalid-data",
            status_code = status.HTTP_400_BAD_REQUEST,
        )
    if request.data.get('permission') == 'public':
        document.is_public = True
    elif request.data.get('permission') == 'private':
        document.is_public = False
    document.save()
    return response(
        message="Document Updated successfully",
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
    
    shared_list = Permission.objects.filter(document=document)

    return response(
        message='list fetched successfully',
        status="list-fetch-successfully",
        status_code=status.HTTP_200_OK,
        content={
            'shared_list': serializers.PermissionSerializer(shared_list, many=True).data
        }
    )