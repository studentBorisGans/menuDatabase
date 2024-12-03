from django.db.models import Prefetch, Avg
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
import json



class MenuService:
    # Since this is only for single inserts (no bulk operations) no need for using update. 
    # .save() method instead
    @staticmethod
    def get_or_create_restaurant(restaurant_data):
        """Gets or creates a restaurant entry."""
        restaurant, created = Restaurants.objects.get_or_create(
            name=restaurant_data.get('name'), defaults={
                "address": restaurant_data.get('address'),
                "phone_number": restaurant_data.get('phone_number'),
                "email": restaurant_data.get('email'),
                "website": restaurant_data.get('website')
            }
        )
        if not created:
            updated = False
            if restaurant_data.get('address') and restaurant_data['address'] != restaurant.address:
                restaurant.address = restaurant_data['address']
                updated = True
            if restaurant_data.get('phone_number') and restaurant_data['phone_number'] != restaurant.phone_number:
                restaurant.phone_number = restaurant_data['phone_number']
                updated = True
            if restaurant_data.get('email') and restaurant_data['email'] != restaurant.email:
                restaurant.email = restaurant_data['email']
                updated = True
            if restaurant_data.get('website') and restaurant_data['website'] != restaurant.website:
                restaurant.website = restaurant_data['website']
                updated = True
            if updated:
                restaurant.save()
                #Maximize efficiency by only writing to DB if changes have been made  
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
    def upload_full_menu(restaurant_data, menu_data, errors):
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


        # ------------------------------------------Full Page ERROR OPTION-----------------------------------------
        # # menu_data = {
        #     "description": <description>, 
        #     "sections": []
        # }

        print(f"Menu Data Received:\n{menu_data}")
        print(f"Restaurant Data Received: \n{restaurant_data}")
        print(f"Erros Received: \n{errors}")

        
        #----------------------ALWAYS EXECUTE; REGARDLESS OF PARSE SUCCESS--------------------
        
        # Get or create the restaurant
        with transaction.atomic():
            restaurant = MenuService.get_or_create_restaurant(restaurant_data)
            restaurant_id = restaurant.restaurant_id

            menu = MenuService.create_menu(restaurant_id, menu_data.get("description"))
            menu_id = menu.menu_id

            # Find current version number for restuarnt, if it exists; fix to point to restuarant
            menu_version = MenuService.create_menu_version(menu_id, menu.description)

            # Indicates no data was collected for file, other than what the user specified in the form
            if errors.get('file_wide'):
                log = MenuService.create_processing_log(menu_version.version_id, "Failed", errors.get('file_wide'))
                return False #Only partial data

            print("Base data uploaded.")
        #----------------------ALWAYS EXECUTE; REGARDLESS OF PARSE SUCCESS--------------------
        
        sections = menu_data.get("sections", [])
        try:
            with transaction.atomic():
                # section_objects = []
                menu_items = []
                dietary_restrictions = []
                item_restrictions = []
                logs = []

                for section_data in sections:
                    section_name = section_data.get('section_name')
                    if not section_name:
                        continue
                    
                    section_save = transaction.savepoint()
                    try:
                        # section = MenuSections(menu_id=menu_id, name=section_name) 
                        section = MenuService.get_or_create_menu_section(menu_id, section_name) #Description add
                        # section_objects.append(section)

                        for item_data in section_data.get('menu_items', []):
                            menu_item = MenuItems(
                                section=section,
                                name=item_data.get("menu_item"),
                                description=item_data.get("description"),
                                price=item_data.get("price"),
                            )
                            menu_items.append(menu_item)

                            dietary_restriction_name = item_data.get("dietary_restriction")
                            if dietary_restriction_name:
                                restriction_save = transaction.savepoint()
                                try:
                                    diet_restriction = DietaryRestrictions(restaurant=restaurant, name=dietary_restriction_name)
                                    dietary_restrictions.append(diet_restriction)
                                    item_restrictions.append(MenuItemDietaryRestrictions(item=menu_item, restriction=diet_restriction))
                                except IntegrityError as e:
                                    print(f"Constraint violation: {e}")
                                    log = MenuProcessingLogs(version=menu_version, status="Partial Fail", error_message="An error occured while uploading dietary restrictions to DB, but everything else was saved.")
                                    logs.append(log)
                                    menu_items.pop()
                                    dietary_restrictions.pop()
                                    item_restrictions.pop()
                                    transaction.savepoint_rollback(restriction_save)
                                    # Only undo this item's dietary restriction actions, in case the error is item specific

                                else:
                                    transaction.savepoint_commit(restriction_save)

                    except Exception as e:
                        print(f"Error processing section: {section_name}")
                        log = MenuProcessingLogs(version=menu_version, status="Partial Fail", error_message="An error occured while uploading a section, but everything else was saved.")
                        logs.append(log)
                        continue
                        # section_objects.pop()
                        # transaction.savepoint_rollback(section_save)
                        # Only undo this sections actions, in case the error is section specific

                # MenuSections.objects.bulk_create(section_objects)
                MenuItems.objects.bulk_create(menu_items)
                DietaryRestrictions.objects.bulk_create(dietary_restrictions)
                MenuItemDietaryRestrictions.objects.bulk_create(item_restrictions)
                MenuProcessingLogs.objects.bulk_create(logs)

            return True
        except Exception as e:
            print(f"Error processing menu data: {e}")
            MenuService.create_processing_log(menu_version.version_id, "Partial Fail", "An unexpected error occured while uploading to DB but your general menu and restuarant info were saved.")
            return False

    @staticmethod
    # For autofill functionality in forms.py
    def get_all_restaurant_data():
        restaurants = Restaurants.objects.all()
        return {
            restaurant.name: {
                "address": restaurant.address or "",
                "phone_number": restaurant.phone_number or "",
                "email": restaurant.email or "",
                "website": restaurant.website or ""
            }
            for restaurant in restaurants
        }

    # efficient


    def get_initial_data():
        # Prefetch related menus and their menu versions and logs
        restaurants = (
            Restaurants.objects.prefetch_related(
                Prefetch(
                    'menus',
                    queryset=Menus.objects.prefetch_related(
                        Prefetch(
                            'versions',
                            queryset=Menu_Versions.objects.prefetch_related(
                                Prefetch(
                                    'processing_logs',
                                    queryset=MenuProcessingLogs.objects.all(),
                                    to_attr='log_list'  # Store logs in a custom attribute
                                )
                            ).order_by('-created_at'),  # Order versions by creation time
                            to_attr='version_list'  # Store versions in a custom attribute
                        )
                    ),
                    to_attr='menu_list'  # Store menus in a custom attribute
                )
            )
        )

        restaurant_data = []

        for restaurant in restaurants:
            menu_list = []
            for menu in restaurant.menu_list:  # Access preloaded menus
                for version in menu.version_list:  # Access preloaded versions
                    # Fetch the first log if it exists
                    log = version.log_list[0] if version.log_list else None
                    status = log.status if log else "Unknown"
                    error_message = log.error_message if log else ""

                    # Append version data to menu list
                    menu_list.append({
                        "menu_id": version.menu_id,
                        "created_at": version.created_at.strftime("%Y-%m-%d at %H:%M:%S"),
                        "description": version.description,
                        "status": status,
                        "error_message": error_message,
                    })

            # Append restaurant data to final structure
            restaurant_data.append({
                "id": restaurant.restaurant_id,
                "name": restaurant.name,
                "address": restaurant.address or "",
                "phone_number": restaurant.phone_number or "",
                "email": restaurant.email or "",
                "website": restaurant.website or "",
                "created_at": restaurant.created_at.strftime("%Y-%m-%d"),
                "menus": menu_list,
            })

        print(f"Restaurant Data: \n{restaurant_data}")
        return restaurant_data


    def get_old_initial_data():

        restaurants = Restaurants.objects.all()
        restaurant_data = []

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
                        "menu_id": version.menu_id,
                        "created_at": version.created_at.strftime("%Y-%m-%d at %H:%M:%S"),
                        "description": version.description,
                        "status": status if not None else "",
                        "error_message": error_message if not None else "",
                    })

            # Append restaurant data to final structure
            restaurant_data.append({
                "id": restaurant.restaurant_id,
                "name": restaurant.name,
                "address": restaurant.address if not None else "",
                "phone_number": restaurant.phone_number if not None else "",
                "email": restaurant.email if not None else "",
                "website": restaurant.website if not None else "",
                "created_at": restaurant.created_at.strftime("%Y-%m-%d"),
                "menus": menu_list,
            })
        print(f"Menu Data: \n{restaurant_data}")

        return restaurant_data
    
    # Done
    def delete_menu(menu_id):
        try:
            with transaction.atomic():
                Menus.objects.filter(menu_id=menu_id).delete()
                # Cascading deletes turned on
            return True
        except Exception as e:
            print(f"Error deleting menu with ID {menu_id}: {e}")
            return False

    def get_menu_data(menu_id):
        menu = (
            Menus.objects.filter(menu_id=menu_id)
            .prefetch_related('sections', 'versions', 'sections__items', 'versions__processing_logs')
        )
        if not menu.exists():
            return {}
        menu_data = menu.first()
        print(f"Menu data: {menu_data}")
        version = menu_data.versions.first()

        menu_json = {
            "version_number": version.version_number,
            "created_at": menu_data.created_at.strftime("%Y-%m-%d at %H:%M:%S"),
            "status": None,
            "error_message": "",
            "description": menu_data.description,
            "sections": [],
        }

        if version.processing_logs.exists():
            log = version.processing_logs.first()
            menu_json["status"] = log.status
            menu_json["error_message"] = log.error_message if log.error_message else ""

        # Fetch the sections and calculate average price per section
        for section in menu_data.sections.all():
            section_data = {
                "section_name": section.name,
                "menu_items": [],
                "avg_section_price": round(float(section.items.aggregate(Avg('price'))['price__avg'] or 0), 2),  # Calculate average price for items in this section
            }

            # Add the menu items for this section
            for menu_item in section.items.all():
                restrict = ""
                if menu_item.menuitemdietaryrestrictions_set.exists():
                    restriction = menu_item.menuitemdietaryrestrictions_set.first()
                    dietaryRestriction = restriction.dietaryrestrictions_set.first()
                    restrict = dietaryRestriction.name
                section_data["menu_items"].append({
                    "menu_item": menu_item.name,
                    "price": float(menu_item.price),
                    "dietary_restriction": restrict,
                    "description": menu_item.description
                })


            # Append the section data to the menu_json object
            menu_json["sections"].append(section_data)

        all_prices = [item['avg_section_price'] for item in menu_json["sections"] if item['avg_section_price'] is not None]
        menu_json["avg_menu_price"] = sum(all_prices) / len(all_prices) if all_prices else 0

        return menu_json

