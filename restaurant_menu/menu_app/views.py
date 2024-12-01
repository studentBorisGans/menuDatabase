# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import pdfplumber
import requests

# from .models import ProcessedData
from .forms import PDFUploadForm
from .utils import PdfParse
# from .utils import process_pdf, send_to_gbt, upload_data


# Create your views here.
def home(request):
    return render(request, 'menu_app/frontend.html')


def handle_pdf_upload(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        # print(form.is_valid)

        if form.is_valid():
            pdf_file = form.return_cleaned_file()
            menuName = form.return_menu_name()
            print(f"Cleaned pdf in views: {pdf_file}")

            parse = PdfParse(pdf_file, menuName)
            response = parse.toImg()

            return JsonResponse({'message': 'PDF processing successful.', 'output': response})
        else:
            return JsonResponse({'error_message': form.return_error_message}, status=400)
    # else:
    form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form})