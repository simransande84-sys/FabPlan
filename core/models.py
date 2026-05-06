from django.db import models # import models from django.db to define database models
from django.contrib.auth.models import User

class Profile(models.Model):
    PROFILE_TYPES = (
        ('frame', 'Frame'),
        ('sash', 'Sash'),
        ('bead', 'Bead'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=PROFILE_TYPES)
    bar_length = models.FloatField(default=6000) # Length in mm
    cost_per_bar = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Hardware(models.Model):
    name = models.CharField(max_length=100)
    typology = models.CharField(max_length=50) # e.g., 'sliding', 'casement'
    quantity_formula = models.CharField(max_length=200, help_text='Formula using "panels" e.g., "2 * panels"')
    price_per_unit = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} for {self.typology}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.code}"

class DesignItem(models.Model):
    PRODUCT_CHOICES = (
        ('window', 'Window'),
        ('door', 'Door'),
    )
    TYPOLOGY_CHOICES = (
        ('sliding', 'Sliding'),
        ('casement', 'Casement'),
        ('fixed', 'Fixed'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='designs')
    product_type = models.CharField(max_length=20, choices=PRODUCT_CHOICES, default='window')
    width = models.FloatField(help_text="Width in mm")
    height = models.FloatField(help_text="Height in mm")
    typology = models.CharField(max_length=20, choices=TYPOLOGY_CHOICES)
    glass_type = models.CharField(max_length=100)
    finish = models.CharField(max_length=100)
    mesh = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)
    number_of_panels = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.get_product_type_display()} - {self.width}x{self.height} (Order: {self.order.code})"

class CutPiece(models.Model):
    design = models.ForeignKey(DesignItem, on_delete=models.CASCADE, related_name='cut_pieces')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    length = models.FloatField(help_text="Length in mm")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.length}mm of {self.profile.name} (Design: {self.design.id})"

class StandardBarLength(models.Model):
    length = models.IntegerField()

    def __str__(self):
        return f"{self.length} mm"

class GlassRate(models.Model):
    glass_type = models.CharField(max_length=100, unique=True)
    price_per_sqm = models.FloatField(default=0)

    def __str__(self):
        return f"{self.glass_type} - ₹{self.price_per_sqm}/sqm"
