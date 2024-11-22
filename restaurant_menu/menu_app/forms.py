from django import forms
from PyPDF2 import PdfReader

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField()

    def is_valid(self):
        print("Validating document...")
        valid = super().is_valid()
        print(f"Validity: {valid}")
        if valid:
            try:
                self.cleaned_data['pdf_file'] = self.clean_pdf()
            except forms.ValidationError as e:
                self.add_error('pdf_file', e)
                return False
            return valid

    def clean_pdf(self):
        print("Cleaning...")
        file = self.cleaned_data.get('pdf_file')
        if not file.name.endswith('.pdf'):
            print("NO PDF")
            raise forms.ValidationError("Only PDF files are allowed.")
        
        reader = PdfReader(file)
        if len(reader.pages) > 10:
            raise forms.ValidationError("Your PDF can have at most 10 pages.")

        return file