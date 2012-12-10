from tastypie.resources import ModelResource
from riversim.models import Simulation

class SimulationResource(ModelResource):
    class Meta:
        queryset = Simulation.objects.all()
        resource_name = 'simulation'
    def dehydrate(self, bundle): 
        bundle.data['lidar_tile_files'] = bundle.obj.lidar_tile_files
        bundle.data['ortho_tile_files'] = bundle.obj.ortho_tile_files
        return bundle
