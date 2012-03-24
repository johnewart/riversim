from django.contrib.gis import geos
from django.db import connection
from django.http import HttpResponse

def log_traceback(exception, args):
    import sys, traceback, logging
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    logging.debug(exception)
    logging.debug(args)
    for tb in traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback):
        logging.debug(tb)

def closest_point(geom1,geom2):
    """
    Use the PostGIS function ST_ClosestPoint() to return the 2-dimensional point on geom1 that is closest to geom2.  This requires
    PostGIS 1.5 or newer.
    """
    cursor = connection.cursor()
    query = "select st_astext( ST_ClosestPoint('%s'::geometry, '%s'::geometry) ) as sline;" % (geom1.wkt, geom2.wkt)
    cursor.execute(query)
    return geos.fromstr(cursor.fetchone()[0])


def render_to_json(*args, **kwargs):
    response = HttpResponse(*args, **kwargs)
    response['mimetype'] = "text/javascript"
    response['Pragma'] = "no cache"
    response['Cache-Control'] = "no-cache, must-revalidate"

    return response