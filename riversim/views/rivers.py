import json
import sys
import re
import os

from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.contrib.gis.shortcuts import render_to_kml, render_to_text
from django.http import HttpResponse, Http404
from django.contrib.gis.geos import Polygon
from django.db.models import Q
from django.template import RequestContext
from django.template import loader

from riversim.models import *

import datetime
import logging

AVAILABLE_LAYERS = { 
        'rivers': {
            'model': River,
            'maxfeatures': 10000
        },
        'lidartiles': {
            'model': LidarTile,
            'maxfeatures': 1000000
        },
        'selectedlidartiles': {
            'model': LidarTile,
            'maxfeatures': 1000000
        }, 
        'cdec_stations': {
            'model': CDECStation,
            'maxfeatures': 10000
        }
}

INVALID_FIELDS = ('the_geom','geom','gml', 'kml', )

def poly_from_bbox(bbox):
    minx,miny,maxx,maxy=[float(i) for i in bbox.split(',')]  # get the coordinates...
    logging.debug("Bounding Box: %s" % bbox)
    bboxpoly = Polygon(((minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny)),srid=4326)
    return bboxpoly


def home(request):
    if request.GET.get("clear_simulation", None):
        try:
            logging.debug("Clearing simulation!")
            del request.session['simulation_id']
        except:
            pass

    rivers = River.objects.filter(type="R").order_by('name').values('name')
    river_names = []
    seen = []
    selected_river_names = request.session.get("river_names", [])

    str_regex = re.compile(r"[A-Za-z]+")
    for river in rivers:
        name = river['name'].split('_')[0]
        if str_regex.match(name) and name not in seen:
            if name in selected_river_names:
                selected = True
            else:
                selected = False
            river_names.append({"name": name, "selected": selected})
            seen.append(name)

    if request.user.is_authenticated():
        simulations = request.user.simulation_set.all()
    else:
        simulations = []

    active_simulation_id = request.session.get('simulation_id', None)

    if active_simulation_id:
        simulation = Simulation.objects.get(pk=active_simulation_id)
    else:
        simulation = None

    params = {
        'river_names' : river_names,
        'simulations' : simulations,
        'simulation' : simulation
    }

    return render_to_response('riversim/map.html', params, context_instance=RequestContext(request))

def filter_rivers(request):
    try:
        bbox = request.GET.get("BBOX", request.GET.get("bbox"))
        if bbox:
            bboxpoly = poly_from_bbox(bbox)
            rivers = River.objects.filter(geom__bboverlaps=bboxpoly)
            jsondata = json.dumps(rivers)
            return HttpResponse(jsondata, status=200)
        else:
            return Http404
    except:
        return HttpResponse(status=500)

def select_rivers(request):
    try:
        river_names = request.GET.getlist("river_names[]")
        request.session['river_names'] = river_names
    except:
        return HttpResponse(status=500)

    return HttpResponse(status=200)

def kml(request, layer=None):
    if layer not in AVAILABLE_LAYERS: 
        raise Http404

    cachefile = None

    try:
        bbox=request.GET.get('BBOX', request.GET.get('bbox')) # Get the BBOX from the WFS request
    except:
        raise Http404            # no bbox? No page for you!

    try:
        minx,miny,maxx,maxy=[float(i) for i in bbox.split(',')]  # get the coordinates...
        logging.debug("Bounding Box: %s" % bbox)
        geom = Polygon(((minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny)),srid=4326)
        logging.debug("GEOM: %s" % geom)
    except:
        logging.debug( "Unexpected error: %s" % sys.exc_info()[0])
        raise Http404

    # Is there an active simulation?
    simulation_id = request.session.get('simulation_id', None)

    if simulation_id:
        logging.debug("Loading rivers for simulation: %d" % simulation_id)
        simulation = Simulation.objects.get(pk=simulation_id)
        river_names = [r.name for r in simulation.rivers.all()]
        geom = simulation.region
    else:
        river_names = []

    logging.debug("River names to filter on: %s" % (river_names))

    features = AVAILABLE_LAYERS[layer]['model'].objects.filter(geom__bboverlaps=geom)
    
    res = []
    
    if (layer == 'rivers'):

        if simulation_id:
            logging.debug("Loading rivers for simulation: %d" % simulation_id)
            simulation = Simulation.objects.get(pk=simulation_id)
            features = simulation.rivers.all()
        else:
            cachefile = os.path.join(settings.MEDIA_ROOT, "cache", "kml", "all_rivers.kml")
            cachedir = os.path.dirname(cachefile)
            if(not os.path.exists(cachedir)):
                os.makedirs(cachedir)

            if os.path.isfile(cachefile):
                kmlfile = open(cachefile)
                logging.debug("Loading KML for rivers from cache: %s" % (cachefile))
                response = HttpResponse(mimetype='application/vnd.google-earth.kml+xml')
                response.write(kmlfile.read())
                return response

            else:
                primary_names =  [r.primary_name for r in features.filter(type="R").order_by('primary_name')]
                print primary_names[0:5]
                primary_names = list(set(primary_names))

                features = []
                for primary_name in primary_names:
                    river = River.objects.filter(primary_name=primary_name).collect()
                    features.append({
                        'name': primary_name,
                        'kml' : river.kml
                    })

    if (layer == 'selectedlidartiles'):

        if len(river_names) == 0:
            features = []
        else:
            try:
                q = Q()
                rivers = River.objects

                for river_name in river_names:
                    logging.debug("Filtering LiDAR tiles on those that touch %s" % (river_name))
                    q |= Q(name__icontains=river_name)

                rivers = rivers.filter(q)

                tileQ = Q()
                for river in rivers:
                    tileQ |= Q(geom__intersects=river.geom)

                features = features.filter(tileQ)

            except:
                logging.debug("Unable to filter tiles on river names")
                logging.debug("Unexpected error: %s" % sys.exc_info()[0])

    if (layer == "cdec_stations"):
        if len(river_names) == 0:
            features = []
        else:
            try:
                station_ids = request.session.get("station_ids", [])

                if(len(station_ids) > 0):
                    features = features.filter(id__in=station_ids)
                else:
                    q = Q()
                    rivers = River.objects

                    for river_name in river_names:
                        logging.debug( "Filtering CDEC stations on those near %s" % (river_name))
                        q |= Q(name__icontains=river_name)

                    rivers = rivers.filter(q)

                    stationQ = Q()
                    stations_nearby = []
                    for river in rivers:
                        stations = CDECStation.objects.filter(geom__dwithin=(river.geom, 0.02))
                        stations_nearby.extend(stations)

                    station_ids = [s.id for s in stations_nearby]
                    features = features.filter(id__in=station_ids)

            except:
                logging.debug( "Unable to filter stations on river names")
                logging.debug( "Unexpected error: %s" % sys.exc_info()[0])


    if len(features) > 0:
        #if kmldata == None:
        #    kmldata = features.kml() # Locate Data..

        try:
            res = features.kml()
        except:
            res = features

        rescount = len(features)
        logging.debug("Result count: %d" % rescount)


        fields={}

        for f in AVAILABLE_LAYERS[layer]['model']._meta.fields:
            if f.name not in INVALID_FIELDS:
                fields[f.name]=f.verbose_name.replace(' ','_')

        if cachefile:
            logging.debug("Writing to cache file: %s" % cachefile)
            cachefile_handle = open(cachefile, "w")
            cachefile_handle.write(loader.render_to_string('riversim/kml/%s.kml' % layer, {'geomdata': res, 'fields': fields}))
            cachefile_handle.close()

        if request.GET.get("debug", False):
            return render_to_response('riversim/kml_dump.html', {'geomdata' : res})

        if rescount < AVAILABLE_LAYERS[layer]['maxfeatures']:   # Limit to 1000 features max
            return render_to_kml('riversim/kml/%s.kml' % layer, {'geomdata': res, 'fields': fields} )
        else:                # too many features to display for this layer
            return render_to_kml('riversim/kml/%s.kml' % layer, {})

    else:
        return HttpResponse(status=404)