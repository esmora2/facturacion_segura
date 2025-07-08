from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'activo', 'roles')
    list_filter = ('activo', 'roles')
    search_fields = ('nombre', 'email')
