
__author__ = 'jewart'

import re

from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.gis.geos import Polygon
from django.db.models import Q

from riversim.models import *
from riversim.forms.runs import EditSimulationForm

import logging, traceback


def create(request):
    if request.GET.get("bbox", None) != None:
        if request.user.is_authenticated():
            try:
                bbox=request.GET.get('BBOX', request.GET.get('bbox')) # Get the BBOX from the WFS request
                minx,miny,maxx,maxy=[float(i) for i in bbox.split(',')]  # get the coordinates...
                bboxpoly = Polygon(((minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny),(minx,miny)),srid=4326)
                logging.debug("Polygon: %s" % (bboxpoly))
                rivers = River.objects.filter(geom__bboverlaps=bboxpoly)
                stations = Station.objects.filter(geom__bboverlaps=bboxpoly)
                simulation = Simulation()
                simulation.name = "New Simulation"
                simulation.user = request.user
                simulation.save()

                # Attach rivers and stations
                simulation.rivers = rivers
                simulation.stations = stations

                # Return URL
                redirect_url = reverse('edit_simulation', kwargs={'simulation_id': simulation.id})
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
        form = EditSimulationForm(request.POST, instance = simulation)
        form.save()
        redirect_url = reverse("show_simulation", kwargs={"simulation_id": simulation.id})
        return HttpResponseRedirect(redirect_url)
    except:
        return HttpResponse(status=500)

def edit(request, simulation_id):
    try:
        simulation = Simulation.objects.get(pk = simulation_id)
        form = EditSimulationForm(instance = simulation)

        params = {
            'form': form,
            'simulation': simulation,
        }
        return render_to_response('riversim/runs/edit.html', params, context_instance=RequestContext(request))
    except Simulation.DoesNotExist:
        return HttpResponseRedirect(reverse('list_runs'))

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
    return render_to_response('riversim/runs/new.html', params, context_instance=RequestContext(request))

def list(request):
    if request.user.is_authenticated():
        runs = request.user.simulation_set.all()
        for simulation in runs:
            simulation.river_names = ", ".join([r.name for r in simulation.rivers.all()])
    else:
        runs = None

    params = {
        'runs': runs
    }
    return render_to_response('riversim/runs/list.html', params, context_instance=RequestContext(request))

def show(request, simulation_id):
    simulation = Simulation.objects.get(pk=simulation_id)
    request.session['river_names'] = [r.name for r in simulation.rivers.all()]
    request.session['station_ids'] = [s.id for s in simulation.stations.all()]

    params = {
        'simulation': simulation
    }


    return render_to_response('riversim/runs/show.html', params, context_instance=RequestContext(request))

