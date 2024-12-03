# Manages URL routing
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.handle_pdf_upload, name='pdf_upload'),
    path('view/', views.view_uploads, name='view_uploads'),
    path('about/', views.about, name='about')

    # path('view_data/', views.handle_pdf_upload, name='upload_pdf')
]