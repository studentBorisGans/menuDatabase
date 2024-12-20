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
    # Since this is only for single inserts (no bulk operations) no need to use update. 
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
                #Minimize operations by only writing to DB if changes have been made  
        return restaurant
    
    @staticmethod
    def get_or_create_dietary_restriction(restaurant, name, description=None):
        dietary_restriction, created = DietaryRestrictions.objects.get_or_create(
            restaurant=restaurant,
            name=name,
            defaults={"description": description}
        )
        return dietary_restriction

    @staticmethod
    def create_menu_section(menu_id, name, description=None):
        """Creates a section for a menu."""
        section = MenuSections.objects.create(
            menu_id=menu_id,
            name=name,
            description=description
        )
        return section

    @staticmethod
    def create_menu(restaurant, description=None):
        """Creates a menu for a restaurant."""
        return Menus.objects.create(restaurant_id=restaurant, description=description)

    @staticmethod
    def create_menu_version(restaurant_id, description=None):
        """Creates a version for a menu."""
        return Menu_Versions.objects.create(
            restaurant_id=restaurant_id, description=description
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
    def create_processing_log(version_id=None, status=None, error_message=None):
        """Creates a processing log for a menu version."""
        return MenuProcessingLogs.objects.create(
            version_id=version_id, status=status, error_message=error_message
        )
    
    @staticmethod
    def upload_full_menu(restaurant_data, menu_data, errors):
        """
        Uploads a complete menu following the defined model structure.
        Parameters:
            - restaurant_data: dict containing restaurant info
            - menu_data: dict containing menu, sections, items, etc.
        """

        print(f"Menu Data Received:\n{menu_data}")
        print(f"Restaurant Data Received: \n{restaurant_data}")
        print(f"Erros Received: \n{errors}")

        #----------------------ALWAYS EXECUTE; REGARDLESS OF PARSE SUCCESS--------------------
        with transaction.atomic():
            restaurant = MenuService.get_or_create_restaurant(restaurant_data)
            restaurant_id = restaurant.restaurant_id

            menu = MenuService.create_menu(restaurant_id, menu_data.get("description"))
            menu_id = menu.menu_id
            print(f'Menu id: {menu_id}')

            # Find current version number for restuarnt, if it exists; fix to point to restuarant
            menu_version = MenuService.create_menu_version(restaurant_id, menu.description)
            menu_version.save()

            # Indicates no data was collected for file, other than what the user specified in the form
            if errors.get('file_wide'):
                log = MenuService.create_processing_log(menu_version.version_id, "Failed", errors.get('file_wide'))
                return

            print("Base data uploaded.")
        #----------------------ALWAYS EXECUTE; REGARDLESS OF PARSE SUCCESS--------------------
        
        sections = menu_data.get("sections", [])
        completeSuccess = True
        try:
            with transaction.atomic():
                item_restrictions = []
                logs = []

                for section_data in sections:
                    section_name = section_data.get('section_name')
                    print(f"\nSection Name: {section_name}")
                    if not section_name:
                        continue
                    
                    section_save = transaction.savepoint()
                    try:
                        section = MenuService.create_menu_section(menu_id, section_name)

                        for item_data in section_data.get('menu_items', []):
                            print(f"Menu_Item: {item_data}")

                            menu_item = MenuService.create_menu_item(section.section_id, item_data.get("menu_item"), item_data.get("description"), item_data.get("price"))
                            dietary_restriction_name = item_data.get("dietary_restriction")
                            if dietary_restriction_name is not None:
                                restriction_save = transaction.savepoint()
                                try:
                                    diet_restriction = MenuService.get_or_create_dietary_restriction(restaurant, dietary_restriction_name)
                                    menu_item_diet_restriction = MenuItemDietaryRestrictions(item=menu_item, restriction=diet_restriction)
                                    item_restrictions.append(menu_item_diet_restriction)

                                except IntegrityError as e:
                                    print(f"Constraint violation: {e}")
                                    completeSuccess = False
                                    log = MenuProcessingLogs(version=menu_version, status="Partial Fail", error_message="An error occured while uploading dietary restriction to DB, but everything else was saved.")

                                    logs.append(log)
                                    item_restrictions.pop()
                                    print(f"Rolling back for {item_data.get("menu_item")}")
                                    transaction.savepoint_rollback(restriction_save)
                                    # Only undo this item's dietary restriction actions, in case the error is item specific
                                else:
                                    transaction.savepoint_commit(restriction_save)

                    except Exception as e:
                        print(f"Error processing section: {section_name}")
                        log = MenuProcessingLogs(version=menu_version, status="Partial Fail", error_message=f"An error occured while uploading a section: {e}")
                        logs.append(log)
                        transaction.savepoint_rollback(section_save)
                        completeSuccess = False
                        continue
                        # Only undo this sections actions, in case the error is section specific
                    else:
                        transaction.savepoint_commit(section_save)


            MenuItemDietaryRestrictions.objects.bulk_create(item_restrictions)
            if completeSuccess:
                MenuService.create_processing_log(menu_version.version_id, "Success")
                logs = []
            else:
                MenuProcessingLogs.objects.bulk_create(logs)
            
            return
        except Exception as e:
            print(f"Error processing menu data: {e}")
            MenuService.create_processing_log(menu_version.version_id, "Partial Fail", "An unexpected error occured while uploading to DB but your general menu and restuarant info were saved.")
            return

    
    # For autofill functionality in forms.py
    @staticmethod
    def get_all_restaurant_data():
        restaurants = Restaurants.objects.values('name', 'address', 'phone_number', 'email', 'website')
        return {
            restaurant.get('name'): {
                "address": restaurant.get('address', ""),
                "phone_number": restaurant.get('phone_number', ""),
                "email": restaurant.get('email', ""),
                "website": restaurant.get('website', "")
            }
            for restaurant in restaurants
        }


    def get_initial_data():
        # Prefetch related menus and their menu versions and logs
        restaurants = (
            Restaurants.objects.prefetch_related(
                Prefetch(
                    'menus',
                    queryset=Menus.objects.all(),
                    to_attr='menu_list'
                ),
                Prefetch(
                    'versions',
                    queryset=Menu_Versions.objects.prefetch_related(
                        Prefetch(
                            'processing_logs',
                            queryset=MenuProcessingLogs.objects.all(),
                            to_attr='log_list'
                        )
                    ).order_by('-created_at'),  # Order versions by creation time
                    to_attr='version_list'
                )
            )
        )

        restaurant_data = []

        for restaurant in restaurants:
            menu_list = []
            version_list = []
            combined_list = []
            for menu in restaurant.menu_list:  # Access preloaded menus
                menu_list.append({
                        "menu_id": menu.menu_id,
                        "created_at": menu.created_at.strftime("%Y-%m-%d at %H:%M:%S"),
                        "description": menu.description
                })

            for version in restaurant.version_list:  # Access preloaded versions
                log = version.log_list[0] if version.log_list else None
                status = log.status if log else "Unknown"
                error_message = log.error_message if log else ""

                # Append version data to menu list
                version_list.append({
                    "status": status,
                    "error_message": error_message,
                })
            
            # Combinging version and menu list
            for i, element in enumerate(menu_list):
                combined_list.append({
                    'menu_id': menu_list[i].get('menu_id'),
                    'created_at': menu_list[i].get('created_at'),
                    'description': menu_list[i].get('description'),
                    'status': version_list[i].get('status'),
                    'error_message': version_list[i].get('error_message')
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
                "menus": combined_list,
            })

        print(f"Restaurant Data: \n{restaurant_data}")
        return restaurant_data
    
    def delete_menu(menu_id):
        try:
            with transaction.atomic():
                menu = Menus.objects.filter(menu_id=menu_id).first()
                if not menu:
                    raise ValueError("Menu not found")

                restaurant = menu.restaurant
                if not restaurant:
                    raise ValueError("Restaurant related to menu not found")
                
                menu_version = Menu_Versions.objects.filter(
                    restaurant=restaurant,
                    description=menu.description
                ).first()

                if not menu_version:
                    raise ValueError("Menu version matching the menu not found")

                processing_log = MenuProcessingLogs.objects.filter(version_id=menu_version.version_id).first()
                if processing_log:
                    processing_log.delete()

                # Cascading deletes turned on
                menu_version.delete()
                menu.delete()
                return True
            
        except Exception as e:
            print(f"Error deleting menu with ID {menu_id}: {e}")
            return False

    def get_menu_data(menu_id):
        menu = (
            Menus.objects.filter(menu_id=menu_id)
            .prefetch_related(
                Prefetch(
                    'sections',
                    queryset=MenuSections.objects.prefetch_related(
                        Prefetch(
                            'items',
                            queryset=MenuItems.objects.all(),
                            to_attr='item_list'
                        )
                    ),
                    to_attr='section_list'
                )
            )
        )
        if not menu.exists():
            return {}
        menu_data = menu.first()
        print(f"Menu data: {menu_data}")

        restaurant = menu_data.restaurant
        version = restaurant.versions.order_by('-created_at').first()

        menu_json = {
            "version_number": version.version_number if version else None,
            "created_at": version.created_at.strftime("%Y-%m-%d at %H:%M:%S") if version else None,
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
        try:
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
                        for restriction in menu_item.menuitemdietaryrestrictions_set.all():
                            dietary_restriction = restriction.restriction 
                            restrict = dietary_restriction.name
                            break

                    section_data["menu_items"].append({
                        "menu_item": menu_item.name,
                        "price": float(menu_item.price),
                        "dietary_restriction": restrict,
                        "description": menu_item.description
                    })

                menu_json["sections"].append(section_data)
                
        except Exception as e:
            print(f"Error: {e}")
            return

        all_prices = [item['avg_section_price'] for item in menu_json["sections"] if item['avg_section_price'] is not None]
        menu_json["avg_menu_price"] = sum(all_prices) / len(all_prices) if all_prices else 0

        return menu_json

