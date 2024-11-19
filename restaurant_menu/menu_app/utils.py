# import pdfplumber
# import requests

# def process_pdf(file_path):
#     with pdfplumber.open(file_path) as pdf:
#         text = ""
#         for page in pdf.pages:
#             text += page.extract_text()
#         return text
    
# def send_to_gbt(data):
#     url = ""
#     response = requests.post(url, json={"data": data})
#     return response.json()

# def upload_data(data):
#     processed_data = ProcessedData(data=data)
#     processed_data.save()