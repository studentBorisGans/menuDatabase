import json

from django import forms
from PyPDF2 import PdfReader
from .models import Restaurants

class PDFUploadForm(forms.Form):
    restaurant_name = forms.CharField(max_length=100, required=True, label="Restaurant Name")
    address = forms.CharField(max_length=200, required=False, label="Address")
    phone_number = forms.CharField(max_length=15, required=False, label="Phone Number")
    email = forms.EmailField(required=False, label="Email")
    website = forms.URLField(required=False, label="Website")
    menu_description = forms.CharField(max_length=100, required=True, label="Menu Description")
    pdf_file = forms.FileField(required=True, label="Upload PDF")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_message = None

    def clean_pdf_file(self):
        print("Cleaning...")
        file = self.cleaned_data.get('pdf_file')
        if not file.name.endswith('.pdf'):
            print("NO PDF")
            self.error_message = "Only PDF files are allowed."
            raise forms.ValidationError("Only PDF files are allowed.")
        
        try:
            reader = PdfReader(file)
            if len(reader.pages) > 10:
                self.error_message = "Your PDF can have at most 10 pages."
                raise forms.ValidationError("Your PDF can have at most 10 pages.")
        except Exception as e:
            self.error_message = f"Error reading PDF file: {e}"
            raise forms.ValidationError(f"Error reading PDF file: {e}")

        return file
    
    def clean(self):
        cleaned_data = super().clean()
        menu_description = cleaned_data.get('menu_description')

        if not menu_description:
            raise forms.ValidationError("Please enter a description for the menu.")

        return cleaned_data

    def is_valid(self):
        print("Validating document...")
        valid = super().is_valid()
        print(f"Validity: {valid}")

        if not valid:
            print("Django could not validate form.")
            return False
        
        try:
            self.cleaned_file = self.cleaned_data.get('pdf_file')
            print(f"Cleaned file in is_valid: {self.cleaned_file}")
            return True
        except forms.ValidationError as e:
            self.error_message = e
            self.add_error('pdf_file', e)

        print("Error in custom form validation.")
        return False
    
    def return_cleaned_file(self):
        return self.cleaned_file
    
    def return_menu_name(self):
        return self.cleaned_data.get('menu_description')
    
    def return_error_message(self):
        return self.error_message 
    
    def return_restaurant_info(self):
        if not self.is_valid():
            print("Form errors:", self.errors)
            return None
        return {
            "name": self.cleaned_data.get("restaurant_name"),
            "address": self.cleaned_data.get("address"),
            "phone_number": self.cleaned_data.get("phone_number"),
            "email":self.cleaned_data.get("email"),
            "website":self.cleaned_data.get("website"),
        }
    
