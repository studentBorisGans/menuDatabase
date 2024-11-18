# Manages URL routing
from django.urls import path
from .views import home, handle_pdf_upload

urlpatterns = [
    path('', home, name='home'),
    path('upload/', handle_pdf_upload, name='upload_pdf')
]