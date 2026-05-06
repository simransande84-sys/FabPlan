from django.contrib import admin
from .models import Profile, Hardware, Order, DesignItem, CutPiece, StandardBarLength, GlassRate

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'bar_length', 'cost_per_bar')
    list_filter = ('type',)

@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'typology', 'quantity_formula', 'price_per_unit')
    list_filter = ('typology',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'customer_name', 'created_at')
    search_fields = ('code', 'customer_name', 'user__username')
    list_filter = ('user', 'created_at')

@admin.register(DesignItem)
class DesignItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_user', 'product_type', 'typology', 'width', 'height', 'quantity', 'number_of_panels')
    list_filter = ('product_type', 'typology', 'order__user')

    def get_user(self, obj):
        return obj.order.user.username if obj.order.user else 'No User'
    get_user.short_description = 'User'

@admin.register(CutPiece)
class CutPieceAdmin(admin.ModelAdmin):
    list_display = ('design', 'profile', 'length', 'quantity')
    list_filter = ('profile',)

@admin.register(StandardBarLength)
class StandardBarLengthAdmin(admin.ModelAdmin):
    list_display = ('length',)

@admin.register(GlassRate)
class GlassRateAdmin(admin.ModelAdmin):
    list_display = ('glass_type', 'price_per_sqm')
