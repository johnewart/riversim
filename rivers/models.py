from django.contrib.gis.geos import Point
from django.contrib.gis.db import models

import datetime 

from riversim.utils import cdec

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

class Sensor(models.Model):
    station = models.ForeignKey(Station)
    type = models.ForeignKey(SensorType)

    def __str__(self):
        return "%s :: %s" % (self.station, self.type)

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
            raise "Unable to update sensor data!"

    def update_sensor_list(self):
        cdec.get_station_sensors(self)

    def save(self):
        super(CDECStation, self).save()
        self.update_sensor_list()
 
    def __str__(self):
        return "CDEC Station '%s'" % (self.station_id)

class River(models.Model):
    gid = models.AutoField(primary_key=True)
    arc_status = models.IntegerField()
    arc_identi = models.IntegerField()
    name = models.CharField(max_length = 65)
    min_x_axis = models.FloatField()
    max_x_axis = models.FloatField()
    min_y_axis = models.FloatField()
    max_y_axis = models.FloatField()
    arc_stat_1 = models.IntegerField()
    arc_iden_1 = models.IntegerField()
    min_x_ax_1 = models.FloatField()
    max_x_ax_1 = models.FloatField()
    min_y_ax_1 = models.FloatField()
    max_y_ax_1 = models.FloatField()
    arc_id = models.IntegerField()
    rr = models.CharField(max_length=22)
    huc = models.CharField(max_length=19)
    type = models.CharField(max_length=12)
    segment_le = models.FloatField()
    miles_term = models.FloatField()
    sum_drain_field = models.FloatField(db_column='sum_drain_')
    primary_name = models.CharField(max_length=41, db_column='primary_na')
    open_water = models.CharField(max_length=41)
    primary_co = models.CharField(max_length=22)
    open_wat_1 = models.CharField(max_length=22)
    down_reach = models.CharField(max_length=22)
    dshuc = models.IntegerField()
    up_directi = models.CharField(max_length=12)
    stream_lev = models.IntegerField()
    down_junct = models.IntegerField()
    termid = models.IntegerField()
    terminal_b = models.IntegerField()
    divergence = models.IntegerField()
    sequence_n = models.CharField(max_length=22)
    geom = models.MultiLineStringField(srid=4269, db_column='the_geom')
    objects = models.GeoManager()
    
    
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
    tile = models.CharField(max_length=18)
    northindex = models.IntegerField()
    eastindex = models.IntegerField()
    eastingll = models.IntegerField()
    northingll = models.IntegerField()
    eastingur = models.IntegerField()
    northingur = models.IntegerField()
    name = models.CharField(max_length=254)
    las_file = models.CharField(max_length=254)
    las_path = models.CharField(max_length=254)
    layer = models.CharField(max_length=17)
    north_st = models.IntegerField()
    east_st = models.IntegerField()
    tile_st = models.CharField(max_length=7)
    out_id = models.CharField(max_length=12)
    to = models.CharField(max_length=7)
    del_date = models.CharField(max_length=16)
    desc_field = models.CharField(max_length=254, db_column='desc_')
    entitytype = models.CharField(max_length=254)
    enttypdesc = models.CharField(max_length=254)
    id = models.FloatField()
    guid = models.CharField(max_length=254)
    lyrname = models.CharField(max_length=254)
    lyrdesc = models.CharField(max_length=254)
    centroidx = models.FloatField()
    centroidy = models.FloatField()
    centroidz = models.FloatField()
    numverts = models.FloatField()
    entarea = models.FloatField()
    areaunit = models.CharField(max_length=254)
    affinepara = models.CharField(max_length=64)
    direction = models.CharField(max_length=16)
    lastaffine = models.CharField(max_length=64)
    lastdirect = models.CharField(max_length=16)
    desc1 = models.CharField(max_length=254)
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
    name = models.CharField(max_length=254)
    desc_field = models.CharField(max_length=254)
    entitytype = models.CharField(max_length=254)
    enttypdesc = models.CharField(max_length=254)
    id = models.FloatField()
    guid = models.CharField(max_length=254)
    lyrname = models.CharField(max_length=254)
    lyrdesc = models.CharField(max_length=254)
    centroidx = models.FloatField()
    centroidy = models.FloatField()
    centroidz = models.FloatField()
    numverts = models.FloatField()
    entarea = models.FloatField()
    areaunit = models.CharField(max_length=254)
    affinepara = models.CharField(max_length=64)
    direction = models.CharField(max_length=16)
    lastaffine = models.CharField(max_length=64)
    lastdirect = models.CharField(max_length=16)
    las_file = models.CharField(max_length=254)
    las_path = models.CharField(max_length=254)
    desc1 = models.CharField(max_length=254)
    area = models.FloatField()
    perimeter = models.FloatField()
    dwr_tiles_field = models.FloatField()
    dwr_tiles1 = models.FloatField()
    poly_field = models.FloatField()
    subclass = models.CharField(max_length=13)
    subclass_field = models.FloatField()
    tile = models.CharField(max_length=18)
    eastingll = models.IntegerField()
    northingll = models.IntegerField()
    eastingur = models.IntegerField()
    northingur = models.IntegerField()
    block = models.FloatField()
    northindex = models.IntegerField()
    eastindex = models.IntegerField()
    oid_field = models.IntegerField()
    ortho_subm = models.CharField(max_length=254)
    geom = models.PolygonField(srid=50000,  db_column='the_geom') # Custom SRID for the DWR mappings
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
