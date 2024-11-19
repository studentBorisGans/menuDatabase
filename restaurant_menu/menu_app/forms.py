from django import forms

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField()

    def clean_pdf(self):
        file = self.cleaned_data.get('pdf_file')
        if file and file.content_type != 'application/pdf':
            raise forms.ValidationError("Only PDF files are allowed.")
        return file