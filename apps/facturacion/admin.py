from django.contrib import admin
from .models import Factura, FacturaItem

class FacturaItemInline(admin.TabularInline):
    model = FacturaItem
    extra = 1

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'creador', 'fecha', 'anulada')
    list_filter = ('anulada', 'fecha')
    search_fields = ('creador__username',)
    inlines = [FacturaItemInline]
