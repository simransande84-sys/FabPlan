from django.contrib import admin
from .models import Profile, Hardware, Order, DesignItem, CutPiece

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'bar_length', 'cost_per_bar')
    list_filter = ('type',)

@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'typology', 'quantity_formula')
    list_filter = ('typology',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'customer_name', 'created_at')
    search_fields = ('code', 'customer_name')

@admin.register(DesignItem)
class DesignItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_type', 'typology', 'width', 'height', 'quantity')
    list_filter = ('product_type', 'typology')

@admin.register(CutPiece)
class CutPieceAdmin(admin.ModelAdmin):
    list_display = ('design', 'profile', 'length', 'quantity')
    list_filter = ('profile',)
