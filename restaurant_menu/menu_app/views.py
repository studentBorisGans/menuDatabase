# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import pdfplumber
import requests

# from .models import ProcessedData
from .forms import PDFUploadForm
from .utils import PdfParse
from .operations import MenuService
# from .utils import process_pdf, send_to_gbt, upload_data

fake_restaurant = {
    "name": "Taco Bell",
    "address": "Some address",
    "phone_number": "2830183894",
    "email": "taco@bell",
    "website": "tacobell.com"
}
# restaurant_data = {
        #     "name": <name>,
        #     "address": <address>, nullable
        #     "phone_number": <phone_number>, nullable
        #     "email": <email>, nullable
        #     "website": <website>, nullable
        # }

# Create your views here.
def home(request):
    return render(request, 'menu_app/frontend.html')


def handle_pdf_upload(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)

        if form.is_valid():
            pdf_file = form.return_cleaned_file()
            menuName = form.return_menu_name()
            print(f"Cleaned pdf in views: {pdf_file}")

            parse = PdfParse(pdf_file, menuName)
            status, response = parse.toImg()
            if status:
                DB = MenuService.upload_full_menu(fake_restaurant, response)
                print(f"DB: {DB}")
            else:
                return JsonResponse({'message': 'PDF processing unsuccessful. No DB operations done.'})
            return JsonResponse({'message': 'PDF processing successful.', 'DB Operation': DB})
        else:
            return JsonResponse({'error_message': form.return_error_message}, status=400)
    # else:
    form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form})