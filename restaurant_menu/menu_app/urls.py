# Manages URL routing
from django.urls import path
from . import views
from django.http import JsonResponse
from .operations import MenuService

# API endpoint for viewing a specific menu
def get_menu_data(request, menu_id):
    menu_data = MenuService.get_menu_data(menu_id) 
    return JsonResponse(menu_data)


urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('upload/', views.handle_pdf_upload, name='pdf_upload'),
    path('view/', views.view_uploads, name='view_uploads'),
    path('about/', views.about, name='about'),
    # AJAX Requests
    path('inspect_menu/<int:menu_id>/', views.inspect_menu, name='inspect_menu'),
    path('menu_version/<int:menu_id>/data/', get_menu_data, name='get_menu_data'),
    path('delete_menu/', views.delete_menu, name="delete_menu"),
    path('show_processing/', views.show_processing, name="show_processing")
]