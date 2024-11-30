# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
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
            print(f"Cleaned pdf in views: {pdf_file}")
            parse = PdfParse(pdf_file)
            data = parse.parse()
            if data is not None:
                print(f"Data: {data}")

            return render(request, 'menu_app/upload.html', {'form': form, 'message': 'PDF uploaded!'})
        else:
            return render(request, 'menu_app/upload.html', {'form': form, 'message': 'Invalid file type! Please upload a PDF.'})
    else:
        form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form})