from django.urls import path
from . import views

app_name = "special"

urlpatterns = [
    path('bulk-upload/', views.BulkUploadView.as_view(), name='bulk_upload'),
    path('bulk-tag-upload/', views.BulkTagUploadView.as_view(), name='bulk_tag_upload'),
]