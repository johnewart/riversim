# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm): 
        db.execute("insert into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values (50000, 'DWR', 1, '+proj=utm +zone=10 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=ft +no_defs', '')")
