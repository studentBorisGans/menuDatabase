from django.db import models

class Restaurants(models.Model):
    restaurant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Menus(models.Model):
    menu_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, related_name='menus')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Menu for {self.restaurant.name}"

class MenuSections(models.Model):
    section_id = models.AutoField(primary_key=True)
    menu = models.ForeignKey(Menus, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Section: {self.name} in {self.menu}"

class MenuItems(models.Model):
    item_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(MenuSections, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class DietaryRestrictions(models.Model):
    restriction_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, related_name='dietary_restrictions')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MenuItemDietaryRestrictions(models.Model):
    item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
    restriction = models.ForeignKey(DietaryRestrictions, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('item', 'restriction')

    def __str__(self):
        return f"{self.item.name} - {self.restriction.name}"

class MenuProcessingLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    menu = models.ForeignKey(Menus, on_delete=models.CASCADE, related_name='processing_logs')
    status = models.CharField(max_length=50)
    error_message = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.menu} - Status: {self.status}"