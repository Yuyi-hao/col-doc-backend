from django.urls import path
from . import views

urlpatterns = [
    # public
    path('public/<uuid:document_slug>', views.read_public_doc, name='read-public-doc'),
    
    # CRUD on shared or own docs
    path('me/documents/', views.get_documents, name='get-doc'),
    path('me/create/', views.create_doc, name='create-doc'),
    path('me/<uuid:document_slug>/edit', views.edit_doc, name='update-doc'),
    path('me/<uuid:document_slug>/view', views.view_doc, name='view-doc'),
    path('me/<uuid:document_slug>/delete', views.delete_doc, name='delete-doc'),

    # document share
    path('me/<uuid:document_slug>/remove_person', views.modify_document_permission , name='remove-person-from-share-list'),
    path('me/<uuid:document_slug>/share_list', views.get_share_list, name='share-list-doc'),

    # request endpoints
    path('me/requests', views.list_requests, name='list-request'),
    path('me/request/<uuid:request_slug>/reply', views.doc_share_request_reply, name='doc-share-request'),
    path('me/requests/<uuid:request_slug>/delete', views.delete_requests, name='delete-request'),

    # permission on docs
    path('me/<uuid:document_slug>/mark_public_or_private', views.mark_doc_public_or_private, name='mark-doc-public-or-private'),
]