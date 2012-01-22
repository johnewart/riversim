from django.contrib.gis import admin
from models import River


class RiverAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'type', 'primary_name')
    list_filter = ('type',)
    search_fields = ['name',]
    

admin.site.register(River, RiverAdmin)