# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Simulation'
        db.create_table('riversim_simulation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('riversim', ['Simulation'])

        # Adding M2M table for field riversim on 'Simulation'
        db.create_table('riversim_simulation_rivers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('simulation', models.ForeignKey(orm['riversim.simulation'], null=False)),
            ('river', models.ForeignKey(orm['riversim.river'], null=False))
        ))
        db.create_unique('riversim_simulation_rivers', ['simulation_id', 'river_id'])

        # Adding M2M table for field stations on 'Simulation'
        db.create_table('riversim_simulation_stations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('simulation', models.ForeignKey(orm['riversim.simulation'], null=False)),
            ('station', models.ForeignKey(orm['riversim.station'], null=False))
        ))
        db.create_unique('riversim_simulation_stations', ['simulation_id', 'station_id'])


    def backwards(self, orm):
        
        # Deleting model 'Simulation'
        db.delete_table('riversim_simulation')

        # Removing M2M table for field riversim on 'Simulation'
        db.delete_table('riversim_simulation_rivers')

        # Removing M2M table for field stations on 'Simulation'
        db.delete_table('riversim_simulation_stations')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'time_window': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riversim.TimeWindow']", 'null': 'True', 'blank': 'True'}),
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
            'duration_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_unit': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sensor_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['riversim.DataSource']", 'null': 'True', 'blank': 'True'})
        },
        'riversim.simulation': {
            'Meta': {'object_name': 'Simulation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rivers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['riversim.River']", 'symmetrical': 'False'}),
            'stations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['riversim.Station']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'riversim.station': {
            'Meta': {'object_name': 'Station'},
            'elevation': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'db_column': "'the_geom'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated_data': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
