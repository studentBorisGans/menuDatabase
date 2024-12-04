import numpy
print(numpy.__version__)

# https://community.openai.com/t/text-parsing-and-producing-the-stable-json-output/853059/2

# To do:
#   DONE: Restaurant selector in add menu (just pass all current restaurants)
#   DONE: Better view menu page
#   DONE: Test to see if you can update restaurant info
#   DONE: Move errors to seperate structure
#   Implement efficient queries:
#       Upload: Done
# 
#   
#   !!!!!UPDATE DATABASE
#       Menu-Verisons should point to restuarant ID not menu_id
#       There will never be two menus with the same menu_id so its compleltey pointless right now.
#       
#   API endpoint for view.html; live updates for deletion and processing PDFs  
# 
#   Add section description in AI call???

#   Fix dietary restriction; not uploading (fixed I think)
#       Uploads but it doesn't check if one alr exists
#   Edit menu page: push data to DB
#   Delete menu functionality (auto refresh?)
#   