# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import json
import pdfplumber
import requests

# from .models import ProcessedData
from .forms import PDFUploadForm
from .utils import PdfParse
from .operations import MenuService
# from .utils import process_pdf, send_to_gbt, upload_data

# Create your views here.
def home(request):
    return render(request, 'menu_app/frontend.html')

def about(request):
    return render(request, "menu_app/about.html")


def handle_pdf_upload(request):
    data = MenuService.get_all_restaurant_data()
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)

        if form.is_valid():
            pdf_file = form.return_cleaned_file()
            menuName = form.return_menu_name()
            restaurantInfo = form.return_restaurant_info()
            print(f"Form is clean!: {pdf_file}")
            print(f"Form is clean!: {restaurantInfo}")

            parse = PdfParse(pdf_file, menuName)
            status, response = parse.toImg()
            if status:
                DB = MenuService.upload_full_menu(restaurantInfo, response)
                print(f"DB: {DB}")
            else: #Clean up...
                return JsonResponse({'message': 'PDF processing unsuccessful. No DB operations done.', 'error_message': ''})
            return JsonResponse({'message': 'PDF processing successful.', 'restaurant_data': data, 'DB Operation': DB, 'error_message': ''})
        else:
            return JsonResponse({'message': 'Invalid form submission', 'restaurant_data': data, 'error_message': form.return_error_message}, status=400)
        
    form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form, 'restaurant_data': data})
# add restuarant data.

def view_uploads(request):
    if request.method == 'POST':
        # Filter logic
        return "post"
    else:
        # Base case; render file initially
        data = MenuService.get_initial_data()
        return render(request, 'menu_app/view.html', {'menu_data': data})

