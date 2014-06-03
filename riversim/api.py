from tastypie.resources import ModelResource
from riversim.models import Simulation, ChannelMap, ChannelWidthMap, AerialMap
from tastypie import http, fields
from django.conf import settings

class SimulationResource(ModelResource):
    class Meta:
        queryset = Simulation.objects.all()
        resource_name = 'simulation'

    def dehydrate(self, bundle): 
        bundle.data['lidar_tile_files'] = bundle.obj.lidar_tile_files
        bundle.data['ortho_tile_files'] = bundle.obj.ortho_tile_files
        try:
            bundle.data['channel_map_id'] = bundle.obj.channelmap.id
        except ChannelMap.DoesNotExist:
            bundle.data['channel_map_id'] = None

        try:
            bundle.data['channel_width_map_id'] = bundle.obj.channelwidthmap.id
        except ChannelWidthMap.DoesNotExist:
            bundle.data['channel_width_map_id'] = None

        try:
            bundle.data['aerial_map_id'] = bundle.obj.aerialmap.id
        except AerialMap.DoesNotExist:
            bundle.data['aerial_map_id'] = None

        return bundle

class ImageMapResource(ModelResource):
    def dehydrate(self, bundle):
        bundle.data['filename'] = bundle.obj.filename
        bundle.data['full_thumbnail_path'] = bundle.obj.thumbnail_path(settings.MAX_AERIAL_IMAGE_WIDTH)
        bundle.data['full_thumbnail_width'] = settings.MAX_AERIAL_IMAGE_WIDTH
        return bundle


class ChannelMapResource(ImageMapResource):
    class Meta:
        queryset = ChannelMap.objects.all()
        resource_name = "channel_map"

class ChannelWidthMapResource(ImageMapResource):
    class Meta:
        queryset = ChannelWidthMap.objects.all()
        resource_name = "channel_width_map"

class AerialMapResource(ImageMapResource):
    class Meta:
        queryset = AerialMap.objects.all()
        resource_name = "aerial_map"