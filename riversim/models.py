from django.contrib.gis.geos import Point
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q

from time import mktime

from riversim.utils import cdec

import datetime 
import json
import os
import sys
import Image
import logging

from gearman import GearmanClient

class DataSource(models.Model):
    name = models.CharField(max_length = 255)

class SensorType(models.Model):
    name = models.CharField(max_length = 255)
    description = models.TextField()
    measurement_unit = models.CharField(max_length = 100)
    sensor_id = models.CharField(max_length=100) # Arbitrary identifier for external data
    source = models.ForeignKey(DataSource, blank=True, null=True, on_delete=models.SET_NULL)
    duration_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "%s (%s) via %s" % (self.name, self.measurement_unit, self.source.name)

class Station(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation  = models.FloatField()
    geom = models.PointField(srid=4326, db_column='the_geom')
    sensor_types = models.ManyToManyField(SensorType, through='Sensor')
    objects = models.GeoManager()
    last_updated_data = models.DateTimeField(null = True, blank = True)

    def save(self):
        self.geom = Point(self.longitude, self.latitude)
        super(Station, self).save()

    def __str__(self):
        if self.cdecstation:
            return self.cdecstation.station_id
        else:
            return "Lat: %f, Long: %f" % (self.latitude, self.longitude)

class Sensor(models.Model):
    station = models.ForeignKey(Station)
    type = models.ForeignKey(SensorType)

    # Filters for chart_data property
    start_date = None
    end_date = None

    def __str__(self):
        return "%s :: %s" % (self.station, self.type)

    def setDataWindow(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def getChartData(self):
        data = []
        measurements = self.measurement_set

        if (self.start_date != None):
            measurements.filter(timestamp__gte = self.start_date)

        if (self.end_date != None):
            measurements.filter(timestamp__lte = self.end_date)


        for measurement in measurements.order_by('timestamp'):
            point = {
                'x': mktime(measurement.timestamp.timetuple()),
                #'x': measurement.timestamp.strftime("%Y-%m-%d %H:%M"),
                'y': measurement.value,
            }
            data.append(point)

        if len(data) == 0:
            return None
        else:
            return data

    chart_data = property(getChartData)

class TimeWindow(models.Model):


    name = models.CharField(max_length=100)
    duration = models.IntegerField() # Time in seconds that this time window covers

class Measurement(models.Model):
    sensor = models.ForeignKey(Sensor)
    time_window = models.ForeignKey(TimeWindow, blank=True, null=True, on_delete=models.SET_NULL)
    value = models.FloatField()
    timestamp = models.DateTimeField()

class CDECStation(Station):
    station_id = models.CharField(max_length = 8)
    river_basin = models.CharField(max_length = 255)
    hydrologic_area = models.CharField(max_length = 255)
    operator = models.CharField(max_length = 255)
    county = models.CharField(max_length = 255) 
    nearby_city = models.CharField(max_length = 255)

    objects = models.GeoManager()


    def update_sensor_data(self):
        try:
            start_date = self.last_updated_data
            if start_date == None:
                start_date = datetime.date.today() - datetime.timedelta(days = 7)
            end_date = datetime.datetime.today()
            cdec.get_all_sensor_data(self, start_date, end_date)
            self.last_updated_data = datetime.datetime.now()
            self.save()
        except:
            raise

    def update_sensor_list(self):
        cdec.get_station_sensors(self)

    def save(self):
        super(CDECStation, self).save()
        self.update_sensor_list()
 
    def __str__(self):
        return "CDEC Station '%s'" % (self.station_id)

class River(models.Model):
    gid = models.AutoField(primary_key=True)
    arc_status = models.IntegerField(null=True, blank=True)
    arc_identi = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length = 65, null=True, blank=True)
    min_x_axis = models.FloatField(null=True, blank=True)
    max_x_axis = models.FloatField(null=True, blank=True)
    min_y_axis = models.FloatField(null=True, blank=True)
    max_y_axis = models.FloatField(null=True, blank=True)
    arc_stat_1 = models.IntegerField(null=True, blank=True)
    arc_iden_1 = models.IntegerField(null=True, blank=True)
    min_x_ax_1 = models.FloatField(null=True, blank=True)
    max_x_ax_1 = models.FloatField(null=True, blank=True)
    min_y_ax_1 = models.FloatField(null=True, blank=True)
    max_y_ax_1 = models.FloatField(null=True, blank=True)
    arc_id = models.IntegerField(null=True, blank=True)
    rr = models.CharField(max_length=22, null=True, blank=True)
    huc = models.CharField(max_length=19, null=True, blank=True)
    type = models.CharField(max_length=12, null=True, blank=True)
    segment_le = models.FloatField(null=True, blank=True)
    miles_term = models.FloatField(null=True, blank=True)
    sum_drain_field = models.FloatField(db_column='sum_drain_', null=True,
            blank=True)
    primary_name = models.CharField(max_length=41, db_column='primary_na',
            null=True, blank=True)
    open_water = models.CharField(max_length=41, null=True, blank=True)
    primary_co = models.CharField(max_length=22, null=True, blank=True)
    open_wat_1 = models.CharField(max_length=22, null=True, blank=True)
    down_reach = models.CharField(max_length=22, null=True, blank=True)
    dshuc = models.IntegerField(null=True, blank=True)
    up_directi = models.CharField(max_length=12, null=True, blank=True)
    stream_lev = models.IntegerField(null=True, blank=True)
    down_junct = models.IntegerField(null=True, blank=True)
    termid = models.IntegerField(null=True, blank=True)
    terminal_b = models.IntegerField(null=True, blank=True)
    divergence = models.IntegerField(null=True, blank=True)
    sequence_n = models.CharField(max_length=22, null=True, blank=True)
    geom = models.MultiLineStringField(srid=4269, db_column='the_geom')
    objects = models.GeoManager()

    def __str__(self):
        return self.name

    def to_dict(self):
        attributes = {
            'name': self.name
        }
        return attributes
    
# Auto-generated `LayerMapping` dictionary for River model
river_mapping = {
    'arc_status' : 'ARC_STATUS',
    'arc_identi' : 'ARC_IDENTI',
    'name' : 'NAME',
    'min_x_axis' : 'MIN_X_AXIS',
    'max_x_axis' : 'MAX_X_AXIS',
    'min_y_axis' : 'MIN_Y_AXIS',
    'max_y_axis' : 'MAX_Y_AXIS',
    'arc_stat_1' : 'ARC_STAT_1',
    'arc_iden_1' : 'ARC_IDEN_1',
    'min_x_ax_1' : 'MIN_X_AX_1',
    'max_x_ax_1' : 'MAX_X_AX_1',
    'min_y_ax_1' : 'MIN_Y_AX_1',
    'max_y_ax_1' : 'MAX_Y_AX_1',
    'arc_id' : 'ARC_ID',
    'rr' : 'RR',
    'huc' : 'HUC',
    'type' : 'TYPE',
    'segment_le' : 'SEGMENT_LE',
    'miles_term' : 'MILES_TERM',
    'sum_drain_field' : 'SUM_DRAIN_',
    'primary_name' : 'PRIMARY_NA',
    'open_water' : 'OPEN_WATER',
    'primary_co' : 'PRIMARY_CO',
    'open_wat_1' : 'OPEN_WAT_1',
    'down_reach' : 'DOWN_REACH',
    'dshuc' : 'DSHUC',
    'up_directi' : 'UP_DIRECTI',
    'stream_lev' : 'STREAM_LEV',
    'down_junct' : 'DOWN_JUNCT',
    'termid' : 'TERMID',
    'terminal_b' : 'TERMINAL_B',
    'divergence' : 'DIVERGENCE',
    'sequence_n' : 'SEQUENCE_N',
    'geom' : 'LINESTRING',
}    


class LidarTile(models.Model):
    gid = models.AutoField(primary_key=True)
    tile = models.CharField(max_length=18, blank=True, null=True)
    northindex = models.IntegerField(blank=True, null=True)
    eastindex = models.IntegerField(blank=True, null=True)
    eastingll = models.IntegerField(blank=True, null=True)
    northingll = models.IntegerField(blank=True, null=True)
    eastingur = models.IntegerField(blank=True, null=True)
    northingur = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True)
    las_file = models.CharField(max_length=254, blank=True, null=True)
    las_path = models.CharField(max_length=254, blank=True, null=True)
    layer = models.CharField(max_length=17, blank=True, null=True)
    north_st = models.IntegerField(blank=True,null=True)
    east_st = models.IntegerField(blank=True,null=True)
    tile_st = models.CharField(max_length=7, blank=True, null=True)
    out_id = models.CharField(max_length=12, blank=True, null=True)
    to = models.CharField(max_length=7, blank=True, null=True)
    del_date = models.CharField(max_length=16, blank=True, null=True)
    desc_field = models.CharField(max_length=254, db_column='desc_',
            blank=True, null=True)
    entitytype = models.CharField(max_length=254, blank=True, null=True)
    enttypdesc = models.CharField(max_length=254, blank=True, null=True)
    id = models.FloatField(blank=True, null=True)
    guid = models.CharField(max_length=254, blank=True, null=True)
    lyrname = models.CharField(max_length=254, blank=True, null=True)
    lyrdesc = models.CharField(max_length=254, blank=True, null=True)
    centroidx = models.FloatField(blank=True, null=True)
    centroidy = models.FloatField(blank=True, null=True)
    centroidz = models.FloatField(blank=True, null=True)
    numverts = models.FloatField(blank=True, null=True)
    entarea = models.FloatField(blank=True, null=True)
    areaunit = models.CharField(max_length=254, blank=True, null=True)
    affinepara = models.CharField(max_length=64, blank=True, null=True)
    direction = models.CharField(max_length=16, blank=True, null=True)
    lastaffine = models.CharField(max_length=64, blank=True, null=True)
    lastdirect = models.CharField(max_length=16, blank=True, null=True)
    desc1 = models.CharField(max_length=254, blank=True, null=True)
    geom = models.PolygonField(srid=50000,  db_column='the_geom') # Custom SRID for the DWR mappings
    objects = models.GeoManager()

# Auto-generated `LayerMapping` dictionary for LidarTile model
lidartile_mapping = {
    'tile' : 'Tile',
    'northindex' : 'Northindex',
    'eastindex' : 'Eastindex',
    'eastingll' : 'EastingLL',
    'northingll' : 'NorthingLL',
    'eastingur' : 'EastingUR',
    'northingur' : 'NorthingUR',
    'name' : 'Name',
    'las_file' : 'LAS_File',
    'las_path' : 'LAS_Path',
    'layer' : 'LAYER',
    'north_st' : 'NORTH_ST',
    'east_st' : 'EAST_ST',
    'tile_st' : 'TILE_ST',
    'out_id' : 'OUT_ID',
    'to' : 'TO',
    'del_date' : 'DEL_DATE',
    'desc_field' : 'Desc_',
    'entitytype' : 'EntityType',
    'enttypdesc' : 'EntTypDesc',
    'id' : 'ID',
    'guid' : 'GUID',
    'lyrname' : 'LyrName',
    'lyrdesc' : 'LyrDesc',
    'centroidx' : 'CentroidX',
    'centroidy' : 'CentroidY',
    'centroidz' : 'CentroidZ',
    'numverts' : 'NumVerts',
    'entarea' : 'EntArea',
    'areaunit' : 'AreaUnit',
    'affinepara' : 'AFFINEPARA',
    'direction' : 'DIRECTION',
    'lastaffine' : 'LASTAFFINE',
    'lastdirect' : 'LASTDIRECT',
    'desc1' : 'Desc1',
    'geom' : 'POLYGON',
}

class OrthoTile(models.Model):
    gid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=254, blank=True, null=True)
    desc_field = models.CharField(max_length=254, db_column='desc_', null=True, blank=True)
    entitytype = models.CharField(max_length=254, blank=True, null=True)
    enttypdesc = models.CharField(max_length=254, blank=True, null=True)
    id = models.FloatField(blank=True, null=True)
    guid = models.CharField(max_length=254, blank=True, null=True)
    lyrname = models.CharField(max_length=254, blank=True, null=True)
    lyrdesc = models.CharField(max_length=254, blank=True, null=True)
    centroidx = models.FloatField(blank=True, null=True)
    centroidy = models.FloatField(blank=True, null=True)
    centroidz = models.FloatField(blank=True, null=True)
    numverts = models.FloatField(blank=True, null=True)
    entarea = models.FloatField(blank=True, null=True)
    areaunit = models.CharField(max_length=254, blank=True, null=True)
    affinepara = models.CharField(max_length=64, blank=True, null=True)
    direction = models.CharField(max_length=16, blank=True, null=True)
    lastaffine = models.CharField(max_length=64, blank=True, null=True)
    lastdirect = models.CharField(max_length=16, blank=True, null=True)
    las_file = models.CharField(max_length=254, blank=True, null=True)
    las_path = models.CharField(max_length=254, blank=True, null=True)
    desc1 = models.CharField(max_length=254, blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    perimeter = models.FloatField(blank=True, null=True)
    dwr_tiles_field = models.FloatField( db_column='dwr_tiles_', null=True, blank=True)
    dwr_tiles1 = models.FloatField(blank=True, null=True)
    poly_field = models.FloatField(db_column="poly_", null=True, blank=True)
    subclass = models.CharField(max_length=13, null=True, blank=True)
    subclass_field = models.FloatField(db_column="subclass_", null=True, blank=True)
    tile = models.CharField(max_length=18, blank=True, null=True)
    eastingll = models.IntegerField(blank=True, null=True)
    northingll = models.IntegerField(blank=True, null=True)
    eastingur = models.IntegerField(blank=True, null=True)
    northingur = models.IntegerField(blank=True, null=True)
    block = models.FloatField(blank=True, null=True)
    northindex = models.IntegerField(blank=True, null=True)
    eastindex = models.IntegerField(blank=True, null=True)
    oid_field = models.IntegerField(db_column="oid_", null=True, blank=True)
    ortho_subm = models.CharField(max_length=254, blank=True, null=True)
    geom = models.MultiPolygonField(srid=50000,  db_column='the_geom') # Custom SRID for the DWR mappings
    objects = models.GeoManager()

# Auto-generated `LayerMapping` dictionary for OrthoTile model
orthotile_mapping = {
    'name' : 'Name',
    'desc_field' : 'Desc_',
    'entitytype' : 'EntityType',
    'enttypdesc' : 'EntTypDesc',
    'id' : 'ID',
    'guid' : 'GUID',
    'lyrname' : 'LyrName',
    'lyrdesc' : 'LyrDesc',
    'centroidx' : 'CentroidX',
    'centroidy' : 'CentroidY',
    'centroidz' : 'CentroidZ',
    'numverts' : 'NumVerts',
    'entarea' : 'EntArea',
    'areaunit' : 'AreaUnit',
    'affinepara' : 'AFFINEPARA',
    'direction' : 'DIRECTION',
    'lastaffine' : 'LASTAFFINE',
    'lastdirect' : 'LASTDIRECT',
    'las_file' : 'LAS_File',
    'las_path' : 'LAS_Path',
    'desc1' : 'Desc1',
    'area' : 'AREA',
    'perimeter' : 'PERIMETER',
    'dwr_tiles_field' : 'DWR_TILES_',
    'dwr_tiles1' : 'DWR_TILES1',
    'poly_field' : 'POLY_',
    'subclass' : 'SUBCLASS',
    'subclass_field' : 'SUBCLASS_',
    'tile' : 'TILE',
    'eastingll' : 'EASTINGLL',
    'northingll' : 'NORTHINGLL',
    'eastingur' : 'EASTINGUR',
    'northingur' : 'NORTHINGUR',
    'block' : 'BLOCK',
    'northindex' : 'Northindex',
    'eastindex' : 'Eastindex',
    'oid_field' : 'OID_',
    'ortho_subm' : 'ORTHO_SUBM',
    'geom' : 'POLYGON',
}

class SimulationModel(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    def to_dict(self):
        attributes = {
            'name': self.name, 
            'short_name': self.short_name, 
            'description': self.description
        }
        return attributes

class ModelParameter(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    units = models.CharField(max_length=200)
    description = models.TextField()
    model = models.ForeignKey(SimulationModel)

    def __str__(self):
        return "%s (%s)" % (self.name, self.units)

class Simulation(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200, blank=True, null=True, default="New Simulation")
    rivers = models.ManyToManyField(River)
    stations = models.ManyToManyField(Station)
    model = models.ForeignKey(SimulationModel, blank=True, null=True)
    bbox = models.PolygonField(srid=4326, null=True, blank=True)
    region = models.PolygonField(srid=4326, null=True, blank=True)
    description = models.TextField(blank=True)
    start_point = models.PointField(srid=4326, null=True, blank=True)
    end_point = models.PointField(srid=4326, null=True, blank=True)
    start_elevation = models.FloatField(default=-1.0)
    end_elevation = models.FloatField(default=-1.0)
    channel_width_job_complete = models.BooleanField(default=False)
    channel_width_job_handle = models.CharField(max_length = 255, blank=True, null=True)
    channel_width_x_origin = models.IntegerField(blank=True, null=True)
    channel_width_y_origin = models.IntegerField(blank=True, null=True)
    aerialmap_width = models.IntegerField(blank=True, null=True)
    aerialmap_height = models.IntegerField(blank=True, null=True)
    channel_tile_job_complete = models.BooleanField(default = False)
    channel_tile_job_handle = models.CharField(max_length = 255, blank=True, null=True)
    channel_width_points = models.CharField(max_length = 255, null=True)
    channel_width_natural_width = models.IntegerField(blank = True, null = True)
    channel_width_natural_height = models.IntegerField(blank = True, null = True)
    elevation_map_job_handle = models.CharField(max_length = 255, blank = True, null = True)
    elevation_map_job_complete = models.BooleanField(default = False)

    def get_lidar_tiles(self):
        return LidarTile.objects.filter(geom__bboverlaps=self.region)       

    def get_lidar_tile_files(self):
        file_list = []
        for lidar_tile in self.get_lidar_tiles():
            filename = os.path.join(settings.LIDAR_TILES_PATH, "%s.las" % (lidar_tile.tile))
            file_list.append(filename)

        return file_list


    def get_ortho_tiles(self):
        rivers = self.rivers.all()

        tileQ = Q()
        for river in rivers:
            thegeom = river.geom.buffer(0.01)
            tileQ |= Q(geom__intersects=thegeom)

        return OrthoTile.objects.filter(tileQ).filter(geom__bboverlaps=self.region)

    def get_ortho_tile_files(self):
        file_list = []
        for ortho_tile in self.get_ortho_tiles():
            filename = os.path.join(settings.RIVER_TILES_PATH, "%s.tif" % (ortho_tile.tile))
            file_list.append(filename)

        return file_list

    def _elevation_change(self):
        try:
            return self.start_elevation - self.end_elevation
        except:
            return -1

    lidar_tiles = property(get_lidar_tiles)
    lidar_tile_files = property(get_lidar_tile_files)
    ortho_tiles = property(get_ortho_tiles)
    ortho_tile_files = property(get_ortho_tile_files)
    elevation_change = property(_elevation_change)

    def __str__(self):
        if self.model:
            model_name = self.model.name
        else:
            model_name = "No model"
        return "Simulation #%d -- %s (%s)" % (self.id, self.name, model_name)

    def to_dict(self):
        attributes = {
            'name': self.name,
            'rivers' : [ r.to_dict() for r in self.rivers.all() ],
            'model': self.model.to_dict(),
            'extent': self.region.extent,
            'description': self.description,
            'start_point' : {
                'longitude': self.start_point.x, 
                'latitude': self.start_point.y
            },
            'end_point' : {
                'longitude': self.end_point.x, 
                'latitude': self.end_point.y
            } 
        }
        return attributes

class Run(models.Model):
    simulation = models.ForeignKey(Simulation)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    results = models.TextField(null=True, blank=True)

    def __str__(self):
        time_fmt = "%I:%M:%S @ %m/%d/%Y %p"
        try:
            start_time = self.start_time.strftime(time_fmt)
        except: 
            start_time = "N/A"

        try:
            end_time = self.end_time.strftime(time_fmt)
        except: 
            end_time = 'N/A'

        return "Run #%d Start: %s End: %s" % (self.id, start_time, end_time)

class RunParameter(models.Model):
    model_parameter = models.ForeignKey(ModelParameter)
    value = models.FloatField()
    run = models.ForeignKey(Run)

    def __str__(self):
        return "%f %s" % (self.value, self.model_parameter.units)

class SimulationImageMap(models.Model):
    image_root = None
    thumbnail_root = None
    simulation = models.OneToOneField(Simulation)
    job_handle = models.CharField(max_length = 255, null = True, blank = True)
    job_complete = models.BooleanField(default = False)

    def _filename(self):
        return os.path.join(self.image_root, "%s.tiff" % (self.simulation.id))

    def thumbnail_path(self, width):
        return os.path.join(self.thumbnail_root, str(width), "%s.png" % (self.simulation.id))

    def get_run_parameters(self):
        return {"simulation_id" : self.simulation.id}

    def _job_status(self):
        if os.path.isfile(self.filename):
            self.job_complete = True
            self.save()

        result = {
                'completed': None, 
                'total': None,
                'percentage': 0
                }
        if self.job_complete:
             result['percentage'] = 100
        else:
            from riversim.shortcuts import get_gearman_status
            try:
                res = get_gearman_status(self.job_handle)
                result['completed'] = res.status['numerator']
                result['total'] = res.status['denominator']
                result['percentage'] = (float(res.status['numerator']) / float(res.status['denominator'])) * 100
            except: 
                result['percentage'] = -1

        return result

    def submit_job(self, force = False):
        if(self.job_handle and force == False):
            logging.debug("That job's already been submitted.")
        else: 
            logging.debug("Submitting job to generate %s" % (self.filename))
            client = GearmanClient(settings.GEARMAN_SERVERS)
            jobdata = json.dumps(self.get_run_parameters())
            jobrequest = client.submit_job(self.job_queue, jobdata, background=True)

            self.job_handle = jobrequest.gearman_job.handle
            self.job_complete = False
            self.save()

    def generate(self, options = {}, force = False):
        if not os.path.isfile(self.filename) or force == True:
            self.submit_job(force)
            return None
        else:
            return Image.open(self.filename)

    job_status = property(_job_status)
    filename = property(_filename)

    class Meta:
        abstract = True

class ElevationMap(SimulationImageMap):
    image_root = settings.ELEVATION_MAP_PATH
    thumbnail_root = os.path.join(settings.THUMBNAIL_PATH, "elevation_cache")

    def generate(self, options, force = False):
        from riversim.imagery import elevation_map
        return elevation_map.generate(self, options, force)

    #def get_run_parameters(self):
    #    return {}

class AerialMap(SimulationImageMap):
    image_root = settings.GEOTIFF_PATH
    thumbnail_root = os.path.join(settings.THUMBNAIL_PATH, "aerial_cache")
    width = models.IntegerField(blank = True, null = True)
    height = models.IntegerField(blank = True, null = True)

    def generate(self, options, force = False):
        if not os.path.isfile(self.filename) or force == True:
            from riversim.imagery import aerial_tiles
            img = aerial_tiles.generate(self)
            self.job_complete = True
            self.save()
            return img
        else:
            return Image.open(self.filename)

    #def get_run_parameters(self):
    #    return {}


class ChannelMap(SimulationImageMap):
    image_root = settings.CHANNEL_PATH
    thumbnail_root = os.path.join(settings.THUMBNAIL_PATH, "channel_cache")
    job_queue = "channel_image"

    #def get_run_parameters(self):
    #    return {
    #      'tile_path': settings.RIVER_TILES_PATH,
    #      'geotiff_image': self.simulation.aerialmap.filename, 
    #      'channel_image': self.filename,
    #      'ortho_tiles': [tile.tile for tile in self.simulation.get_ortho_tiles()],
    #      'tile_width': 5000, 
    #      'tile_height': 5000 
    #     }
   

class ChannelWidthMap(SimulationImageMap):
    image_root = settings.CHANNEL_WIDTH_PATH
    job_queue = "channel_width"
    thumbnail_root = os.path.join(settings.THUMBNAIL_PATH, "width_cache")
    image_natural_width = models.IntegerField(blank = True, null = True)
    image_natural_height = models.IntegerField(blank = True, null = True)
    channel_width_points = models.TextField(blank = True, null = True)

    def generate(self, options, force = False):
        if(options != {}):
            self.channel_width_points = json.dumps(options['points'])
            self.image_natural_width = int(options['naturalWidth'])
            self.image_natural_height = int(options['naturalHeight'])
            self.save()
        return super(ChannelWidthMap, self).generate(force = force)
       
    #def get_run_parameters(self):
    #    return {
    #       'channel_image' : self.simulation.channelmap.filename,
    #       'channel_width_image' : self.simulation.channelwidthmap.filename,
    #       'points': self.channel_width_points, 
    #       'natural_width': self.image_natural_width, 
    #       'natural_height': self.image_natural_height
    #    }
