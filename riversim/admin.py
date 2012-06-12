from django.contrib.gis import admin
from models import *

class RiverAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'type', 'primary_name')
    list_filter = ('type',)
    search_fields = ['name',]

class SimulationAdmin(admin.ModelAdmin):
    pass

class SimulationModelAdmin(admin.ModelAdmin):
    pass

class ModelParameterAdmin(admin.ModelAdmin):
    pass

class RunAdmin(admin.ModelAdmin):
    pass

admin.site.register(River, RiverAdmin)
admin.site.register(Simulation, SimulationAdmin)
admin.site.register(SimulationModel, SimulationModelAdmin)
admin.site.register(ModelParameter, ModelParameterAdmin)
admin.site.register(Run, RunAdmin)
