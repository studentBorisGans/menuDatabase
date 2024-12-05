# Handles HTTP requests and responses
from django.shortcuts import render
from .forms import PDFUploadForm
from .utils import PdfParse
from django.http import JsonResponse
from datetime import datetime
from .operations import MenuService

import queue
import json

# Future expansion for threading and live updates:
# from django.http import HttpResponse
# from threading import Thread
# from io import BytesIO
# import pdfplumber
# import requests
# import fitz

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

            global PROCESSING
            PROCESSING.put(process)
            print(f"Queued process: {process}")

            parse = PdfParse(pdf_file, menuName)
            status, response, errors = parse.toImg()
            if status:
                MenuService.upload_full_menu(restaurantInfo, response, errors)

            print(f"Dequed process: {PROCESSING.get()}")
            return render(request, 'menu_app/upload.html', {'form': form, 'restaurant_data': data})

    form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form, 'restaurant_data': data})

def view_uploads(request, menuId=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            menu_id = data.get('menu_id')
            
            if delete_menu(menu_id):
                data = MenuService.get_initial_data()
                return JsonResponse({'menu_data': data})
            else:
                return JsonResponse({'error': "error"})
        except Exception as e:
            print(f"Err: {str(e)}")
            return JsonResponse({'message': f'Error deleting menu: {str(e)}'}, status=500)
    else:
        print("GET")
        data = MenuService.get_initial_data()
        return render(request, 'menu_app/view.html', {'menu_data': data})

def delete_menu(menu_id):    
    delete = MenuService.delete_menu(menu_id)
    if delete:
        return True
    else:
        return False

def inspect_menu(request, menu_id):
    return render(request, 'menu_app/menu_inspect.html', {'menu_id': menu_id})

# Future expansion with threading and live updates
def show_processing(request):
    if request.method == "GET":
        response_data = {
            'processes': []
        }

        iterableQueue = list(PROCESSING.queue)
        for process in iterableQueue:
            print(f"Process: {process}")
            response_data['processes'].append(process)
        return JsonResponse(response_data)

    return JsonResponse({"error": "Invalid request method"}, status=405)


