# Handles HTTP requests and responses
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import json
import pdfplumber
import requests

# from .models import ProcessedData
from .forms import PDFUploadForm
from .utils import PdfParse
from .operations import MenuService
# from .utils import process_pdf, send_to_gbt, upload_data

# TESTING
fake_restaurant = {
    "name": "Taco Bell",
    "address": "Some address",
    "phone_number": "2830183894",
    "email": "taco@bell",
    "website": "tacobell.com"
}
# menu_data_test = {'description': 'Glory Days', 'sections': [{'section_name': 'Kids Menu', 'menu_items': [{'menu_item': 'Cheeseburger', 'price': 7, 'dietary_restriction': None, 'description': 'Served on a soft roll with a side of steamed broccoli.'}, {'menu_item': 'Grilled Cheese', 'price': 6, 'dietary_restriction': 'vegetarian', 'description': 'Melted American cheese between hearty white bread with a side of steamed broccoli.'}, {'menu_item': 'Homemade Mac and Cheese', 'price': 6, 'dietary_restriction': 'vegetarian', 'description': 'Extra cheesy! Served with a side of steamed broccoli.'}, {'menu_item': 'Fried Shrimp', 'price': 8, 'dietary_restriction': None, 'description': 'Six extra crispy fried shrimp served with tartar sauce and a side of steamed broccoli.'}, {'menu_item': 'Grilled Shrimp', 'price': 8, 'dietary_restriction': None, 'description': 'Six grilled shrimp served with cocktail sauce and a side of steamed broccoli.'}, {'menu_item': 'Crispy Chicken Tenders', 'price': 7, 'dietary_restriction': None, 'description': 'Three crispy chicken tenders served with a side of steamed broccoli.'}, {'menu_item': 'Grilled Chicken', 'price': 7, 'dietary_restriction': None, 'description': 'Grilled chicken served with a side of steamed broccoli.'}]}, {'section_name': 'Desserts', 'menu_items': [{'menu_item': 'Ice Cream Sundae', 'price': 3, 'dietary_restriction': None, 'description': 'Vanilla ice cream with hot fudge, whipped cream and a cherry.'}, {'menu_item': 'Ice Cream Slider', 'price': 2.5, 'dietary_restriction': None, 'description': 'Made with vanilla ice cream.'}]}, {'section_name': 'Shark Attack!', 'menu_items': [{'menu_item': 'Shark Attack!', 'price': None, 'dietary_restriction': None, 'description': 'A collectible shark filled with bright red grenadine syrup, inserted into sparkling clear Sprite.'}]}, {'section_name': 'Dipping Sauces', 'menu_items': [{'menu_item': 'BBQ Sauce', 'price': None, 'dietary_restriction': None, 'description': None}, {'menu_item': 'Blue Cheese Dressing', 'price': None, 'dietary_restriction': None, 'description': None}, {'menu_item': 'Ranch Dressing', 'price': None, 'dietary_restriction': None, 'description': None}, {'menu_item': 'Glory Sauce', 'price': None, 'dietary_restriction': None, 'description': None}, {'menu_item': 'Honey Mustard', 'price': None, 'dietary_restriction': None, 'description': None}]}, {'section_name': 'Sides', 'menu_items': [{'menu_item': 'Steamed Broccoli', 'price': 0, 'dietary_restriction': 'vegan', 'description': None}, {'menu_item': 'Seasoned Fries', 'price': 0, 'dietary_restriction': None, 'description': None}, {'menu_item': 'Mashed Potatoes', 'price': 0, 'dietary_restriction': None, 'description': None}, {'menu_item': 'Applesauce', 'price': 0, 'dietary_restriction': 'vegan', 'description': None}]}, {'Error Message': 'Error in page number 1: No JSON block found in content for page number 2..'}]}
menu_data_test = [
    {
        "id": 1,
        "name": "Restaurant A",
        "created_at": "2024-12-01",
        "menus": [
            {
                "version_id": 101,
                "created_at": "2024-12-01T10:00:00",
                "description": "Main menu",
                "status": "Successful"
            },
            {
                "version_id": 102,
                "created_at": "2024-11-25T15:30:00",
                "description": "Holiday menu",
                "status": "Failed"
            }
        ]
    },
    {
        "id": 2,
        "name": "Restaurant B",
        "created_at": "2024-11-20",
        "menus": []
    }
]

# Create your views here.
def home(request):
    return render(request, 'menu_app/frontend.html')

def about(request):
    return render(request, "menu_app/about.html")


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
                return JsonResponse({'message': 'PDF processing unsuccessful. No DB operations done.', 'error_message': ''})
            return JsonResponse({'message': 'PDF processing successful.', 'DB Operation': DB, 'error_message': ''})
        else:
            return JsonResponse({'message': '', 'error_message': form.return_error_message}, status=400)
    # else:
    form = PDFUploadForm()
    return render(request, 'menu_app/upload.html', {'form': form})

def view_uploads(request):
    if request.method == 'POST':
        # Filter logic
        return "post"
    else:
        # Base case; render file initially
        data = MenuService.get_initial_data()
        return render(request, 'menu_app/view.html', {'menu_data': data})

