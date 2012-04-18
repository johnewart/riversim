import re
import os
import sys
import Image
import json

import numpy
import osr
import gdal

from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.db.models import Q
from django.conf import settings

from riversim.models import *
from riversim.forms.simulations import EditSimulationForm
from riversim.utils import closest_point, render_to_json


import logging, traceback

MAX_AERIAL_IMAGE_WIDTH=20000

def create(request):
    if request.GET.get("polygon", None) != None:
        if request.user.is_authenticated():
            try:
                from django.contrib.gis.geos import GEOSGeometry
                polygon_points = request.GET.get('POLYGON', request.GET.get('polygon'))
                polygon = GEOSGeometry(polygon_points)

                rivers = River.objects.filter(geom__bboverlaps=polygon)
                stations = Station.objects.filter(geom__bboverlaps=polygon)
                simulation = Simulation()
                simulation.name = "New Simulation"
                simulation.user = request.user
                simulation.region = polygon
                simulation.save()

                # Attach rivers and stations
                simulation.rivers = rivers
                simulation.stations = stations

                # Return URL
                redirect_url = reverse('show_simulation', kwargs={'simulation_id': simulation.id})
                return HttpResponse(redirect_url, status=200)
            except:
                e = traceback.print_exc()
                logging.debug("Unexpected error... %s" % e)
                return HttpResponse(status=500)
    else:
        e = traceback.print_exc()
        logging.debug("No such user... %s" % e)
        return HttpResponse(status=500)

def update(request, simulation_id):
    try:
        simulation = Simulation.objects.get(pk=simulation_id)

        if request.is_ajax():
            try:
                start_point_text = request.GET.get("start_point", None)
                end_point_text = request.GET.get("end_point", None)

                if start_point_text:
                    start_point = GEOSGeometry('SRID=4326;POINT(%s)' % (start_point_text))
                    simulation.start_point = start_point

                if end_point_text:
                    end_point = GEOSGeometry('SRID=4326;POINT(%s)' % (end_point_text))
                    simulation.end_point = end_point

                simulation.save()
                return HttpResponse(status=200)
            except:
                return HttpResponse(status=500)
        else:
            # Form update
            try:
                form = EditSimulationForm(request.POST, instance = simulation)
                form.save()
                redirect_url = reverse("show_simulation", kwargs={"simulation_id": simulation.id})
                return HttpResponseRedirect(redirect_url)
            except:
                return HttpResponse(status=500)
    except Simulation.DoesNotExist:
        return HttpResponse(status=404)

def edit(request, simulation_id):
    try:
        simulation = Simulation.objects.get(pk = simulation_id)
        form = EditSimulationForm(instance = simulation)

        params = {
            'form': form,
            'simulation': simulation,
        }
        return render_to_response('riversim/simulations/edit.html', params, context_instance=RequestContext(request))
    except Simulation.DoesNotExist:
        return HttpResponseRedirect(reverse('list_simulations'))

def new(request):
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

    params = {
        'river_names' : river_names,
        'rivers': rivers,
    }
    return render_to_response('riversim/simulations/new.html', params, context_instance=RequestContext(request))

def list(request):
    if request.user.is_authenticated():
        simulations = request.user.simulation_set.all()
        for simulation in simulations:
            simulation.river_names = ", ".join([r.name for r in simulation.rivers.all()])
    else:
        simulations = None

    params = {
        'simulations': simulations
    }
    return render_to_response('riversim/simulations/list.html', params, context_instance=RequestContext(request))

def show(request, simulation_id):
    simulation = Simulation.objects.get(pk=simulation_id)
    #request.session['river_names'] = [r.name for r in simulation.rivers.all()]
    #request.session['station_ids'] = [s.id for s in simulation.stations.all()]
    request.session['simulation_id'] = simulation.id

    params = {
        'simulation': simulation
    }


    return render_to_response('riversim/simulations/show.html', params, context_instance=RequestContext(request))

def aerial_image(request, simulation_id):
    return aerial_image_thumbnail(request, simulation_id, MAX_AERIAL_IMAGE_WIDTH)

def aerial_image_thumbnail(request, simulation_id, thumbnail_width):
    logging.debug("Aerial thumbnail width: %s px" % (thumbnail_width))
    try:
        imagename = "%s.png" % (simulation_id)
        thumbnail_width = int(thumbnail_width)

        if (thumbnail_width > MAX_AERIAL_IMAGE_WIDTH):
            thumbnail_width=MAX_AERIAL_IMAGE_WIDTH

        logging.debug("Aerial thumbnail width: %s px" % (thumbnail_width))

        #Before resizing, check to see if there's a cached image
        width_path = str(thumbnail_width)
        thumbfile = os.path.join(settings.MEDIA_ROOT, "aerial_cache", width_path, imagename)
        thumbdir = os.path.dirname(thumbfile)

        if(not os.path.exists(thumbdir)):
            os.makedirs(thumbdir)

        if os.path.isfile(thumbfile):
            aerial_img = Image.open(thumbfile)
            sys.stdout.write("Loading from thumbnail file: " + thumbfile + "\n")
        else:
            fullsizefile = os.path.join(settings.MEDIA_ROOT, "aerial_cache", str(MAX_AERIAL_IMAGE_WIDTH), imagename)
            logging.debug("Full size image: %s" % (fullsizefile))
            # If we have a full-sized cached image, use that rather than re-building the image
            if os.path.isfile(fullsizefile):
                logging.debug("Resizing %s to %d px in width" % (fullsizefile, thumbnail_width))
                img = Image.open(fullsizefile)
                aspect = float(img.size[0]) / float(img.size[1]) #calculate width/height
                aerial_img = img.resize( (thumbnail_width, int(thumbnail_width / aspect)), Image.BICUBIC)
            else:
                tile_path = settings.RIVER_TILES_PATH

                simulation = Simulation.objects.get(pk = simulation_id)
                rivers = simulation.rivers.all()

                tileQ = Q()
                #tiles = []
                for river in rivers:
                    thegeom = river.geom.buffer(0.01)
                    tileQ |= Q(geom__intersects=thegeom)
                    #river_tiles = OrthoTile.objects.filter(geom__dwithin=(river.geom, 0.02))
                    #tiles.extend(river_tiles)
                    #stations = CDECStation.objects.filter(geom__dwithin=(river.geom, 0.02))

                tiles = OrthoTile.objects.filter(tileQ).filter(geom__bboverlaps=simulation.region)

                img_tiles = []
                for tile in tiles:
                    imgfile = "%s/%s.tif" % (tile_path, tile.tile)
                    logging.debug("Tile: %s" % (tile.tile))
                    img_tiles.append(imgfile)

                from utils.image_stitcher import stitch_tiles
                logging.debug("Generating aerial image with width: %d" % (MAX_AERIAL_IMAGE_WIDTH))
                img = stitch_tiles(img_tiles, MAX_AERIAL_IMAGE_WIDTH)
                img.save(fullsizefile, 'PNG')

                print "Saved original image, writing GeoTIFF"
                # Also save full size image as GeoTIFF
                image_extent = tiles.extent()
                print "Extent: %s" % (str(image_extent))
                topleft = Point(image_extent[0], image_extent[3], srid=tiles[0].geom.srid)
                bottomright = Point(image_extent[2], image_extent[1], srid=tiles[0].geom.srid)
                topleft.transform(4326)
                bottomright.transform(4326)

                res_x = abs(bottomright.x - topleft.x) / img.size[0]
                res_y = abs(topleft.y - bottomright.y) / img.size[1]

                geotiff_file = os.path.join(settings.MEDIA_ROOT, "tile_cache", "%s.tiff" % (simulation_id))
                geotiff_dir = os.path.dirname(geotiff_file)
                if(not os.path.exists(geotiff_dir)):
                    os.makedirs(geotiff_dir)
                print "GeoTIFF File: %s" % (geotiff_file)

                pixels = numpy.array(img)
                driver = gdal.GetDriverByName("GTiff")
                geotiff_full_path = os.path.join(settings.BASE_DIR, geotiff_file)
                dst_ds = driver.Create(str(geotiff_full_path), img.size[0], img.size[1], 3, gdal.GDT_Byte)
                # SetGeoTransform [ topleft_x, pixel_width, rotation, topleft_y, rotation, pixel_height]
                dst_ds.SetGeoTransform( [ topleft.x, res_x, 0, topleft.y, 0, -res_y] )

                srs = osr.SpatialReference()
                srs.SetWellKnownGeogCS("WGS84")
                dst_ds.SetProjection( srs.ExportToWkt() )

                print "Writing GeoTIFF file..."
                # write the band
                print "Channel 1 (Red)..."
                dst_ds.GetRasterBand(1).WriteArray(pixels[:,:,0])
                print "Channel 2 (Green)..."
                dst_ds.GetRasterBand(2).WriteArray(pixels[:,:,1])
                print "Channel 3 (Blue)..."
                dst_ds.GetRasterBand(3).WriteArray(pixels[:,:,2])
                #print "Channel 4 (Alpha)..."
                #dst_ds.GetRasterBand(4).WriteArray(pixels[:,:,3])


                print "Resizing..."
                aspect = float(img.size[0]) / float(img.size[1]) #calculate width/height
                aerial_img = img.resize( (thumbnail_width, int(thumbnail_width / aspect)), Image.BICUBIC)


            # Cache image
            aerial_img.save(thumbfile, 'PNG')

        response = HttpResponse(mimetype='image/png')
        aerial_img.save(response, 'PNG')
        return response


    except:
        logging.debug("Unable to find matching ortho tiles...")
        raise
        return HttpResponse(status=500)

def show_run(request, simulation_id, simulation_run_id):
    return HttpResponse(status=200)

def new_run(request, simulation_id):
    simulation = Simulation.objects.get(pk=simulation_id)
    simulation_model = simulation.model
    model_parameters = simulation_model.modelparameter_set.all()

    params = {
        'simulation' : simulation,
        'model_parameters': model_parameters
    }
    return render_to_response('riversim/simulations/new_run.html', params, context_instance=RequestContext(request))

def create_run(request, simulation_id):
    simulation = Simulation.objects.get(pk=simulation_id)
    model = simulation.model
    run = Run.objects.create(simulation=simulation)

    run_data = {
        'simulation_id' : simulation.id,
        'run_id': run.id
    }
    
    # Make this mo' smarter...
    if model.short_name == 'fourpt':
        from riversim.adaptors import fourpt
        fourpt.run(simulation, run)

    return HttpResponse(status=200)

def closest_point_on_river(request):
    longitude = float(request.GET.get("longitude", None))
    latitude = float(request.GET.get("latitude", None))

    logging.debug("Lon/lat: %f/%f" % (longitude, latitude))

    simulation_id = request.session.get("simulation_id", None)
    if simulation_id:
        simulation = Simulation.objects.get(pk=simulation_id)

        if (latitude and longitude):
            marker_point = GEOSGeometry('SRID=4326;POINT(%f %f)' % (longitude, latitude))
            river = simulation.rivers.distance(marker_point).order_by("distance")[0]
            point = closest_point(marker_point, river.geom)
            results = {
                "longitude": point.x,
                "latitude": point.y
            }

            return render_to_json(json.dumps(results))
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)
