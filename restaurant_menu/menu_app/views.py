# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import json
import pdfplumber
import requests
import queue
from datetime import datetime

from .forms import PDFUploadForm
from .utils import PdfParse
from .operations import MenuService

PROCESSING = queue.Queue()

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

            process = {
                'restaurant': restaurantInfo.get('name'),
                'menu': menuName,
                'start': datetime.now().isoformat()
            }
            # show processing
            global PROCESSING
            PROCESSING.put(process)
            print(f"Queued process: {process}")

            parse = PdfParse(pdf_file, menuName)
            status, response, errors = parse.toImg()
            if status:
                MenuService.upload_full_menu(restaurantInfo, response, errors)
                # delete processing and update

            print(f"Dequed process: {PROCESSING.get()}")

            # Call API
    form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form, 'restaurant_data': data})

def view_uploads(request):
    if request.method == 'POST':
        # Filter logic
        return "post"
    else:
        # Base case; render file initially
        data = MenuService.get_initial_data()
        return render(request, 'menu_app/view.html', {'menu_data': data})

def delete_menu(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            menu_id = data.get('menu_id')
            delete = MenuService.delete_menu(menu_id)
            if delete:
                output = {"message": "Menu deleted successfully!"}
            else:
                output = {"message": "Could not delete menu."}

            return JsonResponse(output)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)
    return JsonResponse({"message": "Invalid request method."}, status=400)

def inspect_menu(request, menu_id):
    return render(request, 'menu_app/menu_inspect.html', {'menu_id': menu_id})

def show_processing(request):
    if request.method == "GET":
        response_data = {
            'processes': []
        }
        test_data = {
            'processes': [ {
                'restaurant': 'tacobell',
                'menu': 'tacos',
                'start': datetime.now().isoformat()
                }, 
                {
                'restaurant': 'other',
                'menu': 'other',
                'start': datetime.now().isoformat()
                }  
            ]}
        return JsonResponse(test_data)

        iterableQueue = list(PROCESSING.queue)
        for process in iterableQueue:
            print(f"Process: {process}")
            response_data['processes'].append(process)
        return JsonResponse(response_data)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# def update_processing(request, )

