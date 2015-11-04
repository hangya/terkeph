from django.contrib import admin
from project.terkeph.models import PhUser

class PhUserAdmin(admin.ModelAdmin):
  search_fields = ['name'] 
#  readonly_fields = ['uid', 'name', 'slug']
  list_display = ('name', 'created', 'modified', 'prohardver_link')

admin.site.register(PhUser, PhUserAdmin)

