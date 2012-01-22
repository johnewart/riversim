import sys
import re

from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml, render_to_text
from django.http import HttpResponse
from django.contrib.gis.geos import Polygon
from django.http import Http404
from django.contrib.gis import feeds
from django.db.models import Q
from django.contrib.gis.measure import Distance, D

from riversim.rivers import models

AVAILABLE_LAYERS = { 
        'rivers': { 
            'model': models.River,
            'maxfeatures': 10000
        },
        'lidartiles': {
            'model': models.LidarTile,
            'maxfeatures': 1000000
        },
        'selectedlidartiles': {
            'model': models.LidarTile,
            'maxfeatures': 1000000
        }, 
        'cdec_stations': {
            'model': models.CDECStation,
            'maxfeatures': 10000
        }
}

INVALID_FIELDS = ('the_geom','geom','gml', 'kml', )


def home(request):
    rivers = models.River.objects.filter(type="R").order_by('name').values('name')
    river_names = []
    seen = []
    selected_river_names = request.session.get("river_names", [])

    print "Selected: %s" % (selected_river_names)
    str_regex = re.compile(r"[A-Za-z]+")
    for river in rivers:
        name = river['name'].split('_')[0]
        if str_regex.match(name) and name not in seen:
            if name in selected_river_names:
                print "Found %s in selected rivers" % (name)
                selected = True
            else:
                selected = False
            river_names.append({"name": name, "selected": selected})
            seen.append(name)
                
                
    return render_to_response('rivers/map.html', {'river_names' : river_names})
    
def filter_rivers(request):
    print "NARF: %s" % (request.GET)
    try:
        river_names = request.GET.getlist("river_names[]")
        request.session['river_names'] = river_names
        print "River filter: %s" % (request.session.get("river_names"))
    except:
        return HttpResponse(status=500)

    return HttpResponse(status=200)

def kml(request, layer=None):
    if layer not in AVAILABLE_LAYERS: 
        raise Http404

    try:
        bbox=request.GET.get('BBOX', request.GET.get('bbox')) # Get the BBOX from the WFS request
    except:
        print "SOL!"
        raise Http404            # no bbox? No page for you!

    try:
        minx,miny,maxx,maxy=[float(i) for i in bbox.split(',')]  # get the coordinates...
        print bbox
        geom = Polygon(((minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny)),srid=4326)
        print "GEOM: %s" % geom
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise Http404

    river_names = request.session.get("river_names", [])
    print "River names to filter on: %s" % (river_names)

    features = AVAILABLE_LAYERS[layer]['model'].objects.filter(geom__bboverlaps=geom)
    
    res = []
    
    if (layer == 'rivers'):
        features = features.filter(type='R')
        
        try:
            q = Q() 
            for river_name in river_names:
                print "Filtering rivers on: %s" % (river_name)
                q |= Q(name__icontains=river_name)

            features = features.filter(q)
        except: 
            print "Unable to filter on river names"

    if (layer == 'selectedlidartiles'):
       
        try:
            q = Q() 
            rivers = models.River.objects
            
            for river_name in river_names:
                print "Filtering LiDAR tiles on those that touch %s" % (river_name)
                q |= Q(name__icontains=river_name)

            rivers = rivers.filter(q)

            tileQ = Q()
            for river in rivers:
                tileQ |= Q(geom__intersects=river.geom)
            
            features = features.filter(tileQ)
                
        except: 
            print "Unable to filter tiles on river names"
            print "Unexpected error:", sys.exc_info()[0]

    if (layer == "cdec_stations"):
        try:
            if len(river_names) == 0:
                features = []
            else:
                q = Q() 
                rivers = models.River.objects
                
                for river_name in river_names:
                    print "Filtering CDEC stations on those near %s" % (river_name)
                    q |= Q(name__icontains=river_name)

                rivers = rivers.filter(q)

                stationQ = Q()
                stations_nearby = []
                for river in rivers:
                    stations = models.CDECStation.objects.filter(geom__dwithin=(river.geom, .0005))
                    stations_nearby.extend(stations)
              
                station_ids = [s.id for s in stations_nearby]
                features = features.filter(id__in=station_ids)
                
        except: 
            print "Unable to filter stations on river names"
            print "Unexpected error:", sys.exc_info()[0]

        
    res = features.kml() # Locate Data..

    rescount = features.count()
    print "Result count: %d" % rescount


    fields={}

    for f in AVAILABLE_LAYERS[layer]['model']._meta.fields:
        if f.name not in INVALID_FIELDS:
            fields[f.name]=f.verbose_name.replace(' ','_')
    
    if request.GET.get("debug", False):
        return render_to_response('rivers/kml_dump.html', {'geomdata' : res})

    if rescount < AVAILABLE_LAYERS[layer]['maxfeatures']:   # Limit to 1000 features max 
        return render_to_kml('rivers/kml/%s.kml' % layer, {'geomdata': res, 'fields': fields} )
    else:                # too many features to display for this layer
        return render_to_kml('rivers/kml/%s.kml' % layer, {})
