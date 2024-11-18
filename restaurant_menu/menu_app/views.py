# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
import pdfplumber
import requests

from .models import ProcessedData
from .forms import PDFUploadForm


# Create your views here.
def home(request):
    return HttpResponse("Welcome! Input a PDF:")

def process_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
    
def send_to_gbt(data):
    url = ""
    response = requests.post(url, json={"data": data})
    return response.json()

def upload_data(data):
    processed_data = ProcessedData(data=data)
    processed_data.save()
# put these in utils directory??

def handle_pdf_upload(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']
        pdf_path = save_pdf(pdf_file) #save_pdf??

        processed_data = process_pdf(pdf_path)
        api_response = send_to_gbt(processed_data)
        upload_data(api_response)

        return render(request, 'menu_app/sucess.html', {'data': api_response})
    else:
        form = PDFUploadForm() #what 
        return render(request, 'menu_app/upload_pdf.html', {'form': form})