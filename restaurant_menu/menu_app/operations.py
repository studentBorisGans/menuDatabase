from django.db.models import Q
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
    def create_menu_item(section_id, name, price, description):
        """Creates an item in a menu section."""
        if price is None:
            price = 0.00
        price = round(price, 2) #Ensuring only two decimals
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
    
    @staticmethod
    # Transaction to rollback DB in case of DB error; logs are for processing errors, not DB errors
    @transaction.atomic
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

        # Get or create the restaurant
        restaurant = MenuService.get_or_create_restaurant(restaurant_data)
        restaurant_id = restaurant.restaurant_id

        menu = MenuService.create_menu(restaurant_id, menu_data.get("description"))
        menu_id = menu.menu_id

        # Find current version number for restuarnt, if it exists
        menu_version = MenuService.create_menu_version(menu_id, menu.description)
        version_number = menu_version.version_number

        sections = menu_data.get("sections", [])
        if sections is not None:
            if sections[0].get("section_name") is not None: 
            # Checking for any of the possible error messages
                for sectionVar in sections:
                    section = MenuService.get_or_create_menu_section(menu_id, sectionVar.get("section_name")) #Include description later
                    for menuItemVar in section.get("menu_items"):
                        menuItem = MenuService.create_menu_item(section.section_id, menuItemVar.get("menu_item"), menuItemVar.get("description"), menuItemVar.get("price"))
                        # Use enumerate instead of object for section_id? Faster?
                        if menuItemVar.get("dietary_restiction") is not None:
                            try:
                                dietRestriction = MenuService.get_or_create_dietary_restriction(restaurant_id, menuItemVar.get("dietary_restriction"))
                                itemRestriction = MenuService.create_menu_item_restriction(menuItem.item_id, dietRestriction.restriction_id)
                            except IntegrityError as e:
                                print(f"Constraint violation in Menu_Items_Dietary_Restrictions: {e}")
                                log = MenuService.create_processing_log(menu_version.version_id, "Fail", e)
                                return
                            
                            log = MenuService.create_processing_log(menu_version.version_id, "Success")
            else:
                # SECOND ERROR MESSAGE
                print("SECOND ERROR MESSAGE")
                log = MenuService.create_processing_log(menu_version.version_id, "Fail", sections[0].get("Error Message"))
                return 
        
        else:
            # FIRST ERROR MESSAGE
            print("FIRST ERROR MESSAGE")
            log = MenuService.create_processing_log(menu_version.version_id, "Fail", menu_data.get("Error Message"))
            return 


