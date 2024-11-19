from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register(ProcessedData)
admin.site.register(Restaurants)
admin.site.register(Menus)
admin.site.register(MenuSections)
admin.site.register(MenuItems)
admin.site.register(DietaryRestrictions)
admin.site.register(MenuItemDietaryRestrictions)
admin.site.register(MenuProcessingLogs)





