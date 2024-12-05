# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from threading import Thread
from io import BytesIO
import fitz

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


from django.http import JsonResponse

# def handle_pdf_upload(request):
#     data = MenuService.get_all_restaurant_data()

#     if request.method == 'POST':
#         form = PDFUploadForm(request.POST, request.FILES)

#         if form.is_valid():
#             pdf_file = form.return_cleaned_file()
#             # pdf_file = BytesIO(form_file.read())
#             # pdf_bytes = form_file.read()

#             menu_name = form.return_menu_name()
#             restaurant_info = form.return_restaurant_info()
#             print(f"Form is clean!: {pdf_file}")
#             print(f"Form is clean!: {restaurant_info}")

#             # Add the process to the processing queue
#             process = {
#                 'restaurant': restaurant_info.get('name'),
#                 'menu': menu_name,
#                 'start': datetime.now().isoformat()
#             }

#             global PROCESSING
#             PROCESSING.put(process)
#             print(f"Queued process: {process}")

#             # Process the PDF upload asynchronously
#             # def process_upload():
#             parse = PdfParse(pdf_file, menu_name)
#             status, response, errors = parse.toImg()
#             if status:
#                 MenuService.upload_full_menu(restaurant_info, response, errors)
#             # print(f"Dequed process: {PROCESSING.get()}")

#             # Use threading for asynchronous processing
#             # Thread(target=process_upload).start()

#             # Immediately return a response to the user
#             return JsonResponse({"message": "PDF upload started. Processing in the background."}, status=202)

#     # Render the form if not a POST request
#     form = PDFUploadForm()
#     return render(request, 'menu_app/upload.html', {'form': form, 'restaurant_data': data})


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
            return render(request, 'menu_app/upload.html', {'form': form, 'restaurant_data': data})

            # Call API
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
        # Render the initial page
        print("GET")
        data = MenuService.get_initial_data()
        return render(request, 'menu_app/view.html', {'menu_data': data})


def delete_menu(menu_id):
    # if request.method == "POST":
    
    delete = MenuService.delete_menu(menu_id)
    if delete:
        return True
    else:
        return False

    
    # return JsonResponse({"message": "Invalid request method."}, status=400)

def inspect_menu(request, menu_id):
    return render(request, 'menu_app/menu_inspect.html', {'menu_id': menu_id})

def show_processing(request):
    if request.method == "GET":
        response_data = {
            'processes': []
        }
        # test_data = {
        #     'processes': [ {
        #         'restaurant': 'tacobell',
        #         'menu': 'tacos',
        #         'start': datetime.now().isoformat()
        #         }, 
        #         {
        #         'restaurant': 'other',
        #         'menu': 'other',
        #         'start': datetime.now().isoformat()
        #         }  
        #     ]}
        # return JsonResponse(test_data)

        iterableQueue = list(PROCESSING.queue)
        for process in iterableQueue:
            print(f"Process: {process}")
            response_data['processes'].append(process)
        return JsonResponse(response_data)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# def update_processing(request, )

