import numpy
print(numpy.__version__)

# https://community.openai.com/t/text-parsing-and-producing-the-stable-json-output/853059/2

# To do:
#   DONE: Restaurant selector in add menu (just pass all current restaurants)
#   DONE: Better view menu page
#   DONE: Test to see if you can update restaurant info
#   DONE: Move errors to seperate structure
#   DONE: Implement efficient queries:
#   DONE: Fix dietary restriction; not uploading (fixed I think)
#
#   DONE: UPDATE DATABASE
    #       Menu-Verisons should point to restuarant ID not menu_id
    #       There will never be two menus with the same menu_id so its compleltey pointless right now.
#       
#   DONE: API endpoint for view.html; live updates for deletion 
#           impossible without some crazy shit: and processing PDFs

#   Filters!!
# Versions arent deleting?
# Also: Constraint violation: (1452, 'Cannot add or update a child row: a foreign key constraint fails (`menu_app`.`menu_app_dietaryrestrictions`, CONSTRAINT `menu_app_dietaryrest_restaurant_id_9ec08e7d_fk_menu_app_` FOREIGN KEY (`restaurant_id`) REFERENCES `menu_app_restaurants` (`restaurant_')
# Error processing section: Sides
