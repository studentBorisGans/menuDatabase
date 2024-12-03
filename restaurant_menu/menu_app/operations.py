from django.db.models import Prefetch
from .models import (
    Restaurants,
    Menus,
    Menu_Versions,
    MenuSections,
    MenuItems,
    DietaryRestrictions,
    MenuItemDietaryRestrictions,
    MenuProcessingLogs,
)
from django.db import *
from django.db import transaction



class MenuService:
    @staticmethod
    def get_or_create_restaurant(restaurant_data):
        """Gets or creates a restaurant entry."""
        restaurant, created = Restaurants.objects.get_or_create(
            name=restaurant_data['name'], defaults={
                "address": restaurant_data['address'],
                "phone_number": restaurant_data['phone_number'],
                "email": restaurant_data['email'],
                "website": restaurant_data['website']
            }
        )
        return restaurant

    @staticmethod
    def get_or_create_dietary_restriction(restaurant, name, description=None):
        """Gets or creates a dietary restriction for a restaurant."""
        restriction, created = DietaryRestrictions.objects.get_or_create(
            restaurant_id=restaurant,
            name=name,
            defaults={"description": description},
        )
        return restriction

    # Not possible to have shared menu sections? Unless you have multiple foreign keys per menu_id
    @staticmethod
    def get_or_create_menu_section(menu_id, name, description=None):
        """Gets or creates a section for a menu."""
        section, created = MenuSections.objects.get_or_create(
            menu_id=menu_id, name=name, defaults={"description": description}
        )
        return section

    @staticmethod
    def create_menu(restaurant, description=None):
        """Creates a menu for a restaurant."""
        return Menus.objects.create(restaurant_id=restaurant, description=description)

    @staticmethod
    def create_menu_version(menu_id, description=None):
        """Creates a version for a menu."""
        return Menu_Versions.objects.create(
            menu_id=menu_id, description=description
        )

    @staticmethod
    def create_menu_item(section_id, name, description, price):
        """Creates an item in a menu section."""
        if price is None:
            price = 0.00
        try:
            price = round(float(price), 2) #Ensuring only two decimals
        except ValueError:
            raise ValueError(f"Invalid price value of {name}: {price}.")
        return MenuItems.objects.create(
            section_id=section_id, name=name, description=description, price=price
        )
    
    @staticmethod
    def create_menu_item_restriction(item_id, restriction_id):
        """Creates an item dietary restriction."""
        return MenuItemDietaryRestrictions.objects.create(
            item_id=item_id, restriction_id=restriction_id
        )

    @staticmethod
    def link_item_to_dietary_restriction(item, restriction):
        """Links a menu item to a dietary restriction."""
        return MenuItemDietaryRestrictions.objects.get_or_create(
            item_id=item, restriction_id=restriction
        )

    @staticmethod
    def create_processing_log(version_id=None, status=None, error_message=None):
        """Creates a processing log for a menu version."""
        return MenuProcessingLogs.objects.create(
            version_id=version_id, status=status, error_message=error_message
        )
    
    # Transaction to rollback DB in case of DB error; logs are for processing errors, not DB errors
    @transaction.atomic
    @staticmethod

# Version number auto-incremenet broken?
    def upload_full_menu(restaurant_data, menu_data):
        """
        Uploads a complete menu following the defined model structure.
        Parameters:
            - restaurant_data: dict containing restaurant info
            - menu_data: dict containing menu, sections, items, etc.
        """
        # restaurant_data = {
        #     "name": <name>,
        #     "address": <address>, nullable
        #     "phone_number": <phone_number>, nullable
        #     "email": <email>, nullable
        #     "website": <website>, nullable
        # }
        # menu_data = {
        #     "description": <description>, 
        #     "sections": [{
#                 "section_name": <section_name>,
#                 "menu_items": [ {
#
#                             "menu_item": "Cheesy Double Decker Taco",
#                             "price": null,
#                             "dietary_restriction": null,
#                             "description": null
#                         },
#                 ]
            #  }]
        # }


        # ------------------------------------------ERROR OPTIONS--------------------------------------------
        # menu_data = {
        #     "description": <description>, 
        #     "Error Message": e
        # }

        # # menu_data = {
        #     "description": <description>, 
        #     "sections": [{
                # "Error Message: f"Page number {page + 1} could not be parsed for menu data. It most likley did not have any menu content."
            #  }]
        # }
        # # menu_data = {
        #     "description": <description>, 
        #     "sections": [{
                # "Error Message: f"Error in page number {page}: {self.errorMsg}."
            #  }]
        # }


        print(f"Menu Data Received:\n{menu_data}")
        
        #----------------------ALWAYS EXECUTE; REGARDLESS OF PARSE SUCCESS--------------------
        
        # Get or create the restaurant
        restaurant = MenuService.get_or_create_restaurant(restaurant_data)
        restaurant_id = restaurant.restaurant_id

        menu = MenuService.create_menu(restaurant_id, menu_data.get("description"))
        menu_id = menu.menu_id

        # Find current version number for restuarnt, if it exists
        menu_version = MenuService.create_menu_version(menu_id, menu.description)
        menu_version.save() #Is this right???? Or is accessing version_number before its saved what's breaking the save method?
        version_number = menu_version.version_number
        #----------------------ALWAYS EXECUTE; REGARDLESS OF PARSE SUCCESS--------------------

        completeSuccess = True
        sectionErrors = []

        sections = menu_data.get("sections", [])
        if sections is not None:

            # Checking for any of the possible error messages
            for i, sectionVar in enumerate(sections):
                if sectionVar.get("section_name") is not None:
                    section = MenuService.get_or_create_menu_section(menu_id, sectionVar.get("section_name")) #Include description later?
                    for menuItemVar in sectionVar.get("menu_items"):
                        menuItem = MenuService.create_menu_item(section.section_id, menuItemVar.get("menu_item"), menuItemVar.get("description"), menuItemVar.get("price"))

                        if menuItemVar.get("dietary_restiction") is not None:
                            try:
                                dietRestriction = MenuService.get_or_create_dietary_restriction(restaurant_id, menuItemVar.get("dietary_restriction"))
                                itemRestriction = MenuService.create_menu_item_restriction(menuItem.item_id, dietRestriction.restriction_id)
                            except IntegrityError as e:
                                print(f"Constraint violation in Menu_Items_Dietary_Restrictions: {e}")
                                log = MenuService.create_processing_log(menu_version.version_id, "Fail", f"Constraint violation in Menu_Items_Dietary_Restrictions: {e}")
                                return False #Unrecovable error; DB operation rollsback
                            
                else:
                    # SECOND ERROR MESSAGE; Section specific error; save section numbers and add to logs after
                    print("SECOND ERROR MESSAGE")
                    sectionErrors.append((i+1, sectionVar.get("Error Message")))
                    completeSuccess = False
        
        else:
            # FIRST ERROR MESSAGE; Complete failure, only restuarant data uploaded + menus + menu_versions
            print("FIRST ERROR MESSAGE")
            log = MenuService.create_processing_log(menu_version.version_id, "Fail", menu_data.get("Error Message"))
            completeSuccess = False
            return completeSuccess

        sectionNums = ""
        for error in sectionErrors:
            sectionNums += error[0] + ", "
            sectionErr = sectionErrors[0][1] #Just return the first error message received; otherwise too long
        if len(sectionErrors) >= 1:
            log = MenuService.create_processing_log(menu_version.version_id, "Partial Fail", f"Errors in sections {sectionNums}: {sectionErr}")
        else:
            log = MenuService.create_processing_log(menu_version.version_id, "Success")

        return completeSuccess #Var to denote if partial fail or complete success



# menu_data_test = [
#     {
#         "id": 1,
#         "name": "Restaurant A",
#         "created_at": "2024-12-01",
#         "menus": [
#             {
#                 "version_id": 101,
#                 "created_at": "2024-12-01T10:00:00",
#                 "description": "Main menu",
#                 "status": "Successful"
#             },
#             {
#                 "version_id": 102,
#                 "created_at": "2024-11-25T15:30:00",
#                 "description": "Holiday menu",
#                 "status": "Failed"
#             }
#         ]
#     },
#     {
#         "id": 2,
#         "name": "Restaurant B",
#         "created_at": "2024-11-20",
#         "menus": []
#     }
# ]

    def get_initial_data():

        restaurants = Restaurants.objects.all()
        menu_data = []

        for restaurant in restaurants:
            # Get menus for this restaurant
            menus = Menus.objects.filter(restaurant=restaurant)

            menu_list = []
            for menu in menus:
                # Get menu versions
                versions = Menu_Versions.objects.filter(menu=menu).order_by('-created_at')
                for version in versions:
                    # Fetch processing log for each version
                    log = MenuProcessingLogs.objects.filter(version_id=version.version_id).first()
                    status = log.status if log else "Unknown"
                    error_message = log.error_message if log else None

                    # Append version data to menu list
                    menu_list.append({
                        "version_id": version.version_id,
                        "created_at": version.created_at.strftime("%Y-%m-%d at %H:%M:%S"),
                        "description": version.description,
                        "status": status,
                        "error_message": error_message,
                    })

            # Append restaurant data to final structure
            menu_data.append({
                "id": restaurant.restaurant_id,
                "name": restaurant.name,
                "created_at": restaurant.created_at.strftime("%Y-%m-%d"),
                "menus": menu_list,
            })
        print(f"Menu Data: \n{menu_data}")

        return menu_data
    




