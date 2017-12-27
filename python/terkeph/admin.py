from django.contrib import admin
from terkeph.models import PhUser

@admin.register(PhUser)
class PhUserAdmin(admin.ModelAdmin):
    search_fields = ['name'] 
    #readonly_fields = ['uid', 'name', 'slug']
    list_display = ('name', 'created', 'modified', 'prohardver_link')

