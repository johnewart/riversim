from django.contrib.gis import geos
from django.db import connection
from django.http import HttpResponse
from django.conf import settings

import sys

import gearman, gearman.job
from gearman import GearmanClient


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

def get_gearman_status(job_handle):
    try:
        # Query gearmand
        client = GearmanClient(settings.GEARMAN_SERVERS)
        client.establish_connection(client.connection_list[0])

        # configure the job to request status for - the last four is not needed for Status requests.
        j = gearman.job.GearmanJob(client.connection_list[0], str(job_handle), None, None, None)

        # create a job request 
        jr = gearman.job.GearmanJobRequest(j)
        jr.state = 'CREATED'

        # request the state from gearmand
        res = client.get_job_status(jr)

        # the res structure should now be filled with the status information about the task
        return (float(res.status['numerator']) / float(res.status['denominator'])) * 100
    except: 
        print "Unexpected error:", sys.exc_info()[0]
        return -1


