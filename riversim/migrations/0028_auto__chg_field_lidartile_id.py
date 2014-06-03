# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'LidarTile.id'
        db.alter_column(u'riversim_lidartile', 'id', self.gf('django.db.models.fields.FloatField')(null=True))


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'LidarTile.id'
        raise RuntimeError("Cannot reverse this migration. 'LidarTile.id' and its values cannot be restored.")


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 2, 22, 0, 11, 863943)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 2, 22, 0, 11, 863450)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'riversim.aerialmap': {
            'Meta': {'object_name': 'AerialMap'},
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'simulation': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['riversim.Simulation']", 'unique': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'riversim.cdecstation': {
            'Meta': {'object_name': 'CDECStation', '_ormbases': [u'riversim.Station']},
            'county': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hydrologic_area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nearby_city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'operator': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'river_basin': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'station_id': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            u'station_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['riversim.Station']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'riversim.channelmap': {
            'Meta': {'object_name': 'ChannelMap'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'simulation': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['riversim.Simulation']", 'unique': 'True'})
        },
        u'riversim.channelwidthmap': {
            'Meta': {'object_name': 'ChannelWidthMap'},
            'channel_width_points': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_natural_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'image_natural_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'simulation': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['riversim.Simulation']", 'unique': 'True'})
        },
        u'riversim.datasource': {
            'Meta': {'object_name': 'DataSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'riversim.elevationmap': {
            'Meta': {'object_name': 'ElevationMap'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'simulation': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['riversim.Simulation']", 'unique': 'True'})
        },
        u'riversim.lidartile': {
            'Meta': {'object_name': 'LidarTile'},
            'affinepara': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'areaunit': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'centroidx': ('django.db.models.fields.FloatField', [], {}),
            'centroidy': ('django.db.models.fields.FloatField', [], {}),
            'centroidz': ('django.db.models.fields.FloatField', [], {}),
            'del_date': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'desc1': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'desc_field': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'db_column': "'desc_'", 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'east_st': ('django.db.models.fields.IntegerField', [], {}),
            'eastindex': ('django.db.models.fields.IntegerField', [], {}),
            'eastingll': ('django.db.models.fields.IntegerField', [], {}),
            'eastingur': ('django.db.models.fields.IntegerField', [], {}),
            'entarea': ('django.db.models.fields.FloatField', [], {}),
            'entitytype': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'enttypdesc': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '50000', 'db_column': "'the_geom'"}),
            'gid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'las_file': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'las_path': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'lastaffine': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'lastdirect': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'layer': ('django.db.models.fields.CharField', [], {'max_length': '17', 'null': 'True', 'blank': 'True'}),
            'lyrdesc': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'lyrname': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'north_st': ('django.db.models.fields.IntegerField', [], {}),
            'northindex': ('django.db.models.fields.IntegerField', [], {}),
            'northingll': ('django.db.models.fields.IntegerField', [], {}),
            'northingur': ('django.db.models.fields.IntegerField', [], {}),
            'numverts': ('django.db.models.fields.FloatField', [], {}),
            'out_id': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'tile': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'tile_st': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'})
        },
        u'riversim.measurement': {
            'Meta': {'object_name': 'Measurement'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.Sensor']"}),
            'time_window': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.TimeWindow']", 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'riversim.modelparameter': {
            'Meta': {'object_name': 'ModelParameter'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.SimulationModel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'riversim.orthotile': {
            'Meta': {'object_name': 'OrthoTile'},
            'affinepara': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'area': ('django.db.models.fields.FloatField', [], {}),
            'areaunit': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'block': ('django.db.models.fields.FloatField', [], {}),
            'centroidx': ('django.db.models.fields.FloatField', [], {}),
            'centroidy': ('django.db.models.fields.FloatField', [], {}),
            'centroidz': ('django.db.models.fields.FloatField', [], {}),
            'desc1': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'desc_field': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'db_column': "'desc_'", 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'dwr_tiles1': ('django.db.models.fields.FloatField', [], {}),
            'dwr_tiles_field': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'dwr_tiles_'", 'blank': 'True'}),
            'eastindex': ('django.db.models.fields.IntegerField', [], {}),
            'eastingll': ('django.db.models.fields.IntegerField', [], {}),
            'eastingur': ('django.db.models.fields.IntegerField', [], {}),
            'entarea': ('django.db.models.fields.FloatField', [], {}),
            'entitytype': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'enttypdesc': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '50000', 'db_column': "'the_geom'"}),
            'gid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'id': ('django.db.models.fields.FloatField', [], {}),
            'las_file': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'las_path': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'lastaffine': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'lastdirect': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'lyrdesc': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'lyrname': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'northindex': ('django.db.models.fields.IntegerField', [], {}),
            'northingll': ('django.db.models.fields.IntegerField', [], {}),
            'northingur': ('django.db.models.fields.IntegerField', [], {}),
            'numverts': ('django.db.models.fields.FloatField', [], {}),
            'oid_field': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'oid_'", 'blank': 'True'}),
            'ortho_subm': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {}),
            'poly_field': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'poly_'", 'blank': 'True'}),
            'subclass': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'subclass_field': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'subclass_'", 'blank': 'True'}),
            'tile': ('django.db.models.fields.CharField', [], {'max_length': '18'})
        },
        u'riversim.river': {
            'Meta': {'object_name': 'River'},
            'arc_id': ('django.db.models.fields.IntegerField', [], {}),
            'arc_iden_1': ('django.db.models.fields.IntegerField', [], {}),
            'arc_identi': ('django.db.models.fields.IntegerField', [], {}),
            'arc_stat_1': ('django.db.models.fields.IntegerField', [], {}),
            'arc_status': ('django.db.models.fields.IntegerField', [], {}),
            'divergence': ('django.db.models.fields.IntegerField', [], {}),
            'down_junct': ('django.db.models.fields.IntegerField', [], {}),
            'down_reach': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'dshuc': ('django.db.models.fields.IntegerField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {'srid': '4269', 'db_column': "'the_geom'"}),
            'gid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'huc': ('django.db.models.fields.CharField', [], {'max_length': '19'}),
            'max_x_ax_1': ('django.db.models.fields.FloatField', [], {}),
            'max_x_axis': ('django.db.models.fields.FloatField', [], {}),
            'max_y_ax_1': ('django.db.models.fields.FloatField', [], {}),
            'max_y_axis': ('django.db.models.fields.FloatField', [], {}),
            'miles_term': ('django.db.models.fields.FloatField', [], {}),
            'min_x_ax_1': ('django.db.models.fields.FloatField', [], {}),
            'min_x_axis': ('django.db.models.fields.FloatField', [], {}),
            'min_y_ax_1': ('django.db.models.fields.FloatField', [], {}),
            'min_y_axis': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '65'}),
            'open_wat_1': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'open_water': ('django.db.models.fields.CharField', [], {'max_length': '41'}),
            'primary_co': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'primary_name': ('django.db.models.fields.CharField', [], {'max_length': '41', 'db_column': "'primary_na'"}),
            'rr': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'segment_le': ('django.db.models.fields.FloatField', [], {}),
            'sequence_n': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'stream_lev': ('django.db.models.fields.IntegerField', [], {}),
            'sum_drain_field': ('django.db.models.fields.FloatField', [], {'db_column': "'sum_drain_'"}),
            'termid': ('django.db.models.fields.IntegerField', [], {}),
            'terminal_b': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'up_directi': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'riversim.run': {
            'Meta': {'object_name': 'Run'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'simulation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.Simulation']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'riversim.runparameter': {
            'Meta': {'object_name': 'RunParameter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.ModelParameter']"}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.Run']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'riversim.sensor': {
            'Meta': {'object_name': 'Sensor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.Station']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.SensorType']"})
        },
        u'riversim.sensortype': {
            'Meta': {'object_name': 'SensorType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'duration_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_unit': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sensor_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.DataSource']", 'null': 'True', 'blank': 'True'})
        },
        u'riversim.simulation': {
            'Meta': {'object_name': 'Simulation'},
            'aerialmap_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'aerialmap_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bbox': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'channel_tile_job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'channel_tile_job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'channel_width_job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'channel_width_job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'channel_width_natural_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'channel_width_natural_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'channel_width_points': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'channel_width_x_origin': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'channel_width_y_origin': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'elevation_map_job_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'elevation_map_job_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'end_elevation': ('django.db.models.fields.FloatField', [], {'default': '-1.0'}),
            'end_point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['riversim.SimulationModel']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'New Simulation'", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'region': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'rivers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['riversim.River']", 'symmetrical': 'False'}),
            'start_elevation': ('django.db.models.fields.FloatField', [], {'default': '-1.0'}),
            'start_point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'stations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['riversim.Station']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'riversim.simulationmodel': {
            'Meta': {'object_name': 'SimulationModel'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'riversim.station': {
            'Meta': {'object_name': 'Station'},
            'elevation': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'db_column': "'the_geom'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated_data': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'sensor_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['riversim.SensorType']", 'through': u"orm['riversim.Sensor']", 'symmetrical': 'False'})
        },
        u'riversim.timewindow': {
            'Meta': {'object_name': 'TimeWindow'},
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['riversim']
