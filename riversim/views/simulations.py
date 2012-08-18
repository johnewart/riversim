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

from utils.usgs import *

from riversim.models import *
from riversim.forms.simulations import EditSimulationForm
from riversim.utils import closest_point, render_to_json

from gearman import GearmanClient

import logging, traceback


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
                    simulation.start_elevation = usgs_elevation(start_point.x, start_point.y)


                if end_point_text:
                    end_point = GEOSGeometry('SRID=4326;POINT(%s)' % (end_point_text))
                    simulation.end_point = end_point
                    simulation.end_elevation = usgs_elevation(end_point.x, end_point.y)

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

def thumbnail(request, simulation, image_type, thumbnail_width):
    thumbnail_width = int(thumbnail_width)

    if (thumbnail_width > settings.MAX_AERIAL_IMAGE_WIDTH):
        thumbnail_width = settings.MAX_AERIAL_IMAGE_WIDTH

    logging.debug("Thumbnail width: %s px" % (thumbnail_width))

    thumbfile = simulation.thumbnail_path(image_type, thumbnail_width)
    fullsizefile = simulation.thumbnail_path(image_type, settings.MAX_AERIAL_IMAGE_WIDTH)
    
    thumbdir = os.path.dirname(thumbfile)

    if(not os.path.exists(thumbdir)):
        os.makedirs(thumbdir)
    
    thumb_img = None

    if os.path.isfile(thumbfile):
        thumb_img = Image.open(thumbfile)
        sys.stdout.write("Loading cached thumbnail file: " + thumbfile + "\n")
    else:
        logging.debug("Full size image: %s" % (fullsizefile))
        # If we have a full-sized cached image, use that rather than re-building the image
        if os.path.isfile(fullsizefile):
            logging.debug("Resizing %s to %d px in width" % (fullsizefile, thumbnail_width))
            img = Image.open(fullsizefile)
        else:
            img = simulation.generate_image(image_type)            
            imgdir = os.path.dirname(fullsizefile)
            if (not os.path.exists(imgdir)):
                os.makedirs(imgdir)
            img.save(fullsizefile, 'PNG')

        # Cache image
        aspect = float(img.size[0]) / float(img.size[1]) #calculate width/height
        thumb_img = img.resize( (thumbnail_width, int(thumbnail_width / aspect)), Image.BICUBIC)
        thumb_img.save(thumbfile, 'PNG')

    response = HttpResponse(mimetype='image/png')
    thumb_img.save(response, 'PNG')
    return response


def channel_image(request, simulation_id): 
    return channel_image_thumbnail(request, simulation_id, settings.MAX_AERIAL_IMAGE_WIDTH)

def channel_image_thumbnail(request, simulation_id, thumbnail_width):
    simulation = Simulation.objects.get(pk=simulation_id)
    return thumbnail(request, simulation, "channel", thumbnail_width)

def aerial_image(request, simulation_id):
    return aerial_image_thumbnail(request, simulation_id, settings.MAX_AERIAL_IMAGE_WIDTH)

def aerial_image_thumbnail(request, simulation_id, thumbnail_width):
    simulation = Simulation.objects.get(pk=simulation_id)
    return thumbnail(request, simulation, "aerial", thumbnail_width)

def channel_width_image(request, simulation_id):
    return channel_width_image_thumbnail(request, simulation_id, settings.MAX_AERIAL_IMAGE_WIDTH)

def channel_width_image_thumbnail(request, simulation_id, thumbnail_width): 
    simulation = Simulation.objects.get(pk = simulation_id)
    response_image = None

    if simulation.channel_width_job_complete:
        response_image = thumbnail(request, simulation, 'width', thumbnail_width)
    else:
        if not simulation.channel_width_job_handle:
            actual_x = int(request.GET.get('actualX'))
            actual_y = int(request.GET.get('actualY'))
            natural_width = int(request.GET.get('naturalWidth'))
            natural_height = int(request.GET.get('naturalHeight'))
            start_x = (actual_x / natural_width) * simulation.aerialmap_width
            start_y = (actual_y / natural_height) * simulation.aerialmap_height

            simulation.channel_width_x_origin = start_x
            simulation.channel_width_y_origin = start_y
            simulation.save()

            simulation.generate_image('width')

    
    if request.is_ajax(): 
        if response_image:
            response_data = {
                'channel_width_image' : request.path
            }
        else: 
            response_data = {
                'percent_complete' : simulation.get_channel_width_status()
            }
        json_data = json.dumps(response_data)
        return HttpResponse(json_data, mimetype="application/json")
    else:
        return thumbnail(request, simulation, "width", thumbnail_width)

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

    for param in request.POST:
        result = re.match(r'model_params_(\w+)', param)
        if result:
            short_name = result.groups()[0]
            value = float(request.POST.get(param))
            model_param = ModelParameter.objects.get(model = model, short_name = short_name)
            run_param = RunParameter.create(value = value, run = run, model_parameter = model_param)

    params = {
        'simulation_id' : simulation.id,
        'run_id': run.id
    }
    
    # TODO: Make this mo' smarter...
    if model.short_name == 'fourpt':
        from riversim.adaptors import fourpt
        fourpt.run(simulation, run)

    redirect_url = reverse("show_run", kwargs={"run_id": run.id})
    return HttpResponseRedirect(redirect_url)

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
