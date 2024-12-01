from django import forms
from PyPDF2 import PdfReader

class PDFUploadForm(forms.Form):
    menu_name = forms.CharField(max_length=100, required=True, label="Menu Name")
    pdf_file = forms.FileField()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaned_file = None
        self.error_message = None


    def is_valid(self):
        print("Validating document...")
        valid = super().is_valid()
        print(f"Validity: {valid}")

        if valid:
            try:
                self.cleaned_file = self.clean_pdf()
                print(f"Cleaned file in is_valid: {self.cleaned_file}")
                return True
            except forms.ValidationError as e:
                self.error_message = e
                self.add_error('pdf_file', e)
            print("Error in PDF Upload Form is_valid")
            return False

    def clean_pdf(self):
        print("Cleaning...")
        file = self.cleaned_data.get('pdf_file')
        if not file.name.endswith('.pdf'):
            print("NO PDF")
            self.error_message = "Only PDF files are allowed."
            raise forms.ValidationError("Only PDF files are allowed.")
        if self.cleaned_data.get('menu_name') is " ":
            self.error_message = "Please enter a name for the menu."
            raise forms.ValidationError("Please enter a name for the menu.")
        
        try:
            reader = PdfReader(file)
            if len(reader.pages) > 10:
                self.error_message = "Your PDF can have at most 10 pages."
                raise forms.ValidationError("Your PDF can have at most 10 pages.")
        except Exception as e:
            self.error_message = f"Error reading PDF file: {e}"
            raise forms.ValidationError(f"Error reading PDF file: {e}")

        return file
    
    def return_cleaned_file(self):
        return self.cleaned_file
    
    def return_menu_name(self):
        return self.cleaned_data.get('menu_name')
    
    def return_error_message(self):
        return self.error_message 