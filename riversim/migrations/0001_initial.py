# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DataSource'
        db.create_table('riversim_datasource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('riversim', ['DataSource'])

        # Adding model 'SensorType'
        db.create_table('riversim_sensortype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('measurement_unit', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sensor_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riversim.DataSource'])),
        ))
        db.send_create_signal('riversim', ['SensorType'])

        # Adding model 'Station'
        db.create_table('riversim_station', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('elevation', self.gf('django.db.models.fields.FloatField')()),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PointField')(db_column='the_geom')),
        ))
        db.send_create_signal('riversim', ['Station'])

        # Adding model 'Sensor'
        db.create_table('riversim_sensor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riversim.Station'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riversim.SensorType'])),
        ))
        db.send_create_signal('riversim', ['Sensor'])

        # Adding model 'TimeWindow'
        db.create_table('riversim_timewindow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('riversim', ['TimeWindow'])

        # Adding model 'Measurement'
        db.create_table('riversim_measurement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riversim.Sensor'])),
            ('time_window', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['riversim.TimeWindow'])),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('riversim', ['Measurement'])

        # Adding model 'CDECStation'
        db.create_table('riversim_cdecstation', (
            ('station_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['riversim.Station'], unique=True, primary_key=True)),
            ('station_id', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('river_basin', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('hydrologic_area', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('operator', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('nearby_city', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('riversim', ['CDECStation'])

        # Adding model 'River'
        db.create_table('riversim_river', (
            ('gid', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('arc_status', self.gf('django.db.models.fields.IntegerField')()),
            ('arc_identi', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=65)),
            ('min_x_axis', self.gf('django.db.models.fields.FloatField')()),
            ('max_x_axis', self.gf('django.db.models.fields.FloatField')()),
            ('min_y_axis', self.gf('django.db.models.fields.FloatField')()),
            ('max_y_axis', self.gf('django.db.models.fields.FloatField')()),
            ('arc_stat_1', self.gf('django.db.models.fields.IntegerField')()),
            ('arc_iden_1', self.gf('django.db.models.fields.IntegerField')()),
            ('min_x_ax_1', self.gf('django.db.models.fields.FloatField')()),
            ('max_x_ax_1', self.gf('django.db.models.fields.FloatField')()),
            ('min_y_ax_1', self.gf('django.db.models.fields.FloatField')()),
            ('max_y_ax_1', self.gf('django.db.models.fields.FloatField')()),
            ('arc_id', self.gf('django.db.models.fields.IntegerField')()),
            ('rr', self.gf('django.db.models.fields.CharField')(max_length=22)),
            ('huc', self.gf('django.db.models.fields.CharField')(max_length=19)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('segment_le', self.gf('django.db.models.fields.FloatField')()),
            ('miles_term', self.gf('django.db.models.fields.FloatField')()),
            ('sum_drain_field', self.gf('django.db.models.fields.FloatField')(db_column='sum_drain_')),
            ('primary_name', self.gf('django.db.models.fields.CharField')(max_length=41, db_column='primary_na')),
            ('open_water', self.gf('django.db.models.fields.CharField')(max_length=41)),
            ('primary_co', self.gf('django.db.models.fields.CharField')(max_length=22)),
            ('open_wat_1', self.gf('django.db.models.fields.CharField')(max_length=22)),
            ('down_reach', self.gf('django.db.models.fields.CharField')(max_length=22)),
            ('dshuc', self.gf('django.db.models.fields.IntegerField')()),
            ('up_directi', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('stream_lev', self.gf('django.db.models.fields.IntegerField')()),
            ('down_junct', self.gf('django.db.models.fields.IntegerField')()),
            ('termid', self.gf('django.db.models.fields.IntegerField')()),
            ('terminal_b', self.gf('django.db.models.fields.IntegerField')()),
            ('divergence', self.gf('django.db.models.fields.IntegerField')()),
            ('sequence_n', self.gf('django.db.models.fields.CharField')(max_length=22)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiLineStringField')(srid=4269, db_column='the_geom')),
        ))
        db.send_create_signal('riversim', ['River'])

        # Adding model 'LidarTile'
        db.create_table('riversim_lidartile', (
            ('gid', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tile', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('northindex', self.gf('django.db.models.fields.IntegerField')()),
            ('eastindex', self.gf('django.db.models.fields.IntegerField')()),
            ('eastingll', self.gf('django.db.models.fields.IntegerField')()),
            ('northingll', self.gf('django.db.models.fields.IntegerField')()),
            ('eastingur', self.gf('django.db.models.fields.IntegerField')()),
            ('northingur', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('las_file', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('las_path', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('layer', self.gf('django.db.models.fields.CharField')(max_length=17)),
            ('north_st', self.gf('django.db.models.fields.IntegerField')()),
            ('east_st', self.gf('django.db.models.fields.IntegerField')()),
            ('tile_st', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('out_id', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('to', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('del_date', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('desc_field', self.gf('django.db.models.fields.CharField')(max_length=254, db_column='desc_')),
            ('entitytype', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('enttypdesc', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('id', self.gf('django.db.models.fields.FloatField')()),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('lyrname', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('lyrdesc', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('centroidx', self.gf('django.db.models.fields.FloatField')()),
            ('centroidy', self.gf('django.db.models.fields.FloatField')()),
            ('centroidz', self.gf('django.db.models.fields.FloatField')()),
            ('numverts', self.gf('django.db.models.fields.FloatField')()),
            ('entarea', self.gf('django.db.models.fields.FloatField')()),
            ('areaunit', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('affinepara', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('lastaffine', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('lastdirect', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('desc1', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=50000, db_column='the_geom')),
        ))
        db.send_create_signal('riversim', ['LidarTile'])

        # Adding model 'OrthoTile'
        db.create_table('riversim_orthotile', (
            ('gid', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('desc_field', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('entitytype', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('enttypdesc', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('id', self.gf('django.db.models.fields.FloatField')()),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('lyrname', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('lyrdesc', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('centroidx', self.gf('django.db.models.fields.FloatField')()),
            ('centroidy', self.gf('django.db.models.fields.FloatField')()),
            ('centroidz', self.gf('django.db.models.fields.FloatField')()),
            ('numverts', self.gf('django.db.models.fields.FloatField')()),
            ('entarea', self.gf('django.db.models.fields.FloatField')()),
            ('areaunit', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('affinepara', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('lastaffine', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('lastdirect', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('las_file', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('las_path', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('desc1', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('area', self.gf('django.db.models.fields.FloatField')()),
            ('perimeter', self.gf('django.db.models.fields.FloatField')()),
            ('dwr_tiles_field', self.gf('django.db.models.fields.FloatField')()),
            ('dwr_tiles1', self.gf('django.db.models.fields.FloatField')()),
            ('poly_field', self.gf('django.db.models.fields.FloatField')()),
            ('subclass', self.gf('django.db.models.fields.CharField')(max_length=13)),
            ('subclass_field', self.gf('django.db.models.fields.FloatField')()),
            ('tile', self.gf('django.db.models.fields.CharField')(max_length=18)),
            ('eastingll', self.gf('django.db.models.fields.IntegerField')()),
            ('northingll', self.gf('django.db.models.fields.IntegerField')()),
            ('eastingur', self.gf('django.db.models.fields.IntegerField')()),
            ('northingur', self.gf('django.db.models.fields.IntegerField')()),
            ('block', self.gf('django.db.models.fields.FloatField')()),
            ('northindex', self.gf('django.db.models.fields.IntegerField')()),
            ('eastindex', self.gf('django.db.models.fields.IntegerField')()),
            ('oid_field', self.gf('django.db.models.fields.IntegerField')()),
            ('ortho_subm', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=50000, db_column='the_geom')),
        ))
        db.send_create_signal('riversim', ['OrthoTile'])


    def backwards(self, orm):
        
        # Deleting model 'DataSource'
        db.delete_table('riversim_datasource')

        # Deleting model 'SensorType'
        db.delete_table('riversim_sensortype')

        # Deleting model 'Station'
        db.delete_table('riversim_station')

        # Deleting model 'Sensor'
        db.delete_table('riversim_sensor')

        # Deleting model 'TimeWindow'
        db.delete_table('riversim_timewindow')

        # Deleting model 'Measurement'
        db.delete_table('riversim_measurement')

        # Deleting model 'CDECStation'
        db.delete_table('riversim_cdecstation')

        # Deleting model 'River'
        db.delete_table('riversim_river')

        # Deleting model 'LidarTile'
        db.delete_table('riversim_lidartile')

        # Deleting model 'OrthoTile'
        db.delete_table('riversim_orthotile')


    models = {
        'riversim.cdecstation': {
            'Meta': {'object_name': 'CDECStation', '_ormbases': ['riversim.Station']},
            'county': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hydrologic_area': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nearby_city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'operator': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'river_basin': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'station_id': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'station_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['riversim.Station']", 'unique': 'True', 'primary_key': 'True'})
        },
        'riversim.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'riversim.lidartile': {
            'Meta': {'object_name': 'LidarTile'},
            'affinepara': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'areaunit': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'centroidx': ('django.db.models.fields.FloatField', [], {}),
            'centroidy': ('django.db.models.fields.FloatField', [], {}),
            'centroidz': ('django.db.models.fields.FloatField', [], {}),
            'del_date': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'desc1': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'desc_field': ('django.db.models.fields.CharField', [], {'max_length': '254', 'db_column': "'desc_'"}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'east_st': ('django.db.models.fields.IntegerField', [], {}),
            'eastindex': ('django.db.models.fields.IntegerField', [], {}),
            'eastingll': ('django.db.models.fields.IntegerField', [], {}),
            'eastingur': ('django.db.models.fields.IntegerField', [], {}),
            'entarea': ('django.db.models.fields.FloatField', [], {}),
            'entitytype': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'enttypdesc': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '50000', 'db_column': "'the_geom'"}),
            'gid': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'id': ('django.db.models.fields.FloatField', [], {}),
            'las_file': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'las_path': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'lastaffine': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'lastdirect': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'layer': ('django.db.models.fields.CharField', [], {'max_length': '17'}),
            'lyrdesc': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'lyrname': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'north_st': ('django.db.models.fields.IntegerField', [], {}),
            'northindex': ('django.db.models.fields.IntegerField', [], {}),
            'northingll': ('django.db.models.fields.IntegerField', [], {}),
            'northingur': ('django.db.models.fields.IntegerField', [], {}),
            'numverts': ('django.db.models.fields.FloatField', [], {}),
            'out_id': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'tile': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'tile_st': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        },
        'riversim.measurement': {
            'Meta': {'object_name': 'Measurement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riversim.Sensor']"}),
            'time_window': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riversim.TimeWindow']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'riversim.orthotile': {
            'Meta': {'object_name': 'OrthoTile'},
            'affinepara': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'area': ('django.db.models.fields.FloatField', [], {}),
            'areaunit': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'block': ('django.db.models.fields.FloatField', [], {}),
            'centroidx': ('django.db.models.fields.FloatField', [], {}),
            'centroidy': ('django.db.models.fields.FloatField', [], {}),
            'centroidz': ('django.db.models.fields.FloatField', [], {}),
            'desc1': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'desc_field': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'dwr_tiles1': ('django.db.models.fields.FloatField', [], {}),
            'dwr_tiles_field': ('django.db.models.fields.FloatField', [], {}),
            'eastindex': ('django.db.models.fields.IntegerField', [], {}),
            'eastingll': ('django.db.models.fields.IntegerField', [], {}),
            'eastingur': ('django.db.models.fields.IntegerField', [], {}),
            'entarea': ('django.db.models.fields.FloatField', [], {}),
            'entitytype': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'enttypdesc': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '50000', 'db_column': "'the_geom'"}),
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
            'oid_field': ('django.db.models.fields.IntegerField', [], {}),
            'ortho_subm': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {}),
            'poly_field': ('django.db.models.fields.FloatField', [], {}),
            'subclass': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'subclass_field': ('django.db.models.fields.FloatField', [], {}),
            'tile': ('django.db.models.fields.CharField', [], {'max_length': '18'})
        },
        'riversim.river': {
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
        'riversim.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riversim.Station']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riversim.SensorType']"})
        },
        'riversim.sensortype': {
            'Meta': {'object_name': 'SensorType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_unit': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sensor_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'riversim.station': {
            'Meta': {'object_name': 'Station'},
            'elevation': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'db_column': "'the_geom'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'sensor_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['riversim.SensorType']", 'through': "orm['riversim.Sensor']", 'symmetrical': 'False'})
        },
        'riversim.timewindow': {
            'Meta': {'object_name': 'TimeWindow'},
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['riversim']
