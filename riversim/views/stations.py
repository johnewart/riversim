import json

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from riversim.models import *

import datetime
import logging

def station_sensors(request):
    try:
        station_id = request.GET.get("station_id", request.GET.get("STATION_ID"))
        logging.debug("Station ID: %s" % station_id)
        station = Station.objects.get(pk=station_id)
        sensor_types = station.sensor_types.all()
        sensor_names = [s.name for s in sensor_types]
        if(len(sensor_names) > 0):
            jsondata = json.dumps(sensor_names)
            return HttpResponse(jsondata, status=200)
        else:
            return HttpResponse("", status=200)
    except:
        raise
        return HttpResponse(status=500)

def list(request):
    stations = Station.objects.all()

    params = {
        'stations': stations
    }

    return render_to_response('riversim/stations/list.html', params)



def show(request, station_id):
    try:
        station = Station.objects.get(pk=station_id)
        if station.cdecstation:
            station = CDECStation.objects.get(pk=station_id)

    except:
        station = None

    start_date = request.GET.get('start_date', datetime.date.today() - datetime.timedelta(days=7))
    end_date   = request.GET.get('start_date', datetime.date.today())

    sensors = station.sensor_set.all()

    for sensor in sensors:
        sensor.setDataWindow(start_date, end_date)

    params = {
        'station': station,
        'sensors': sensors,
        'start_date': start_date,
        'end_date': end_date,
        }
    return render_to_response('riversim/stations/show.html', params)

def sync(request, station_id):
    station = Station.objects.get(pk=station_id)
    if station.cdecstation:
        cdecstation = station.cdecstation
        cdecstation.update_sensor_list()
        cdecstation.update_sensor_data()
    redirect_url = reverse("show_station", kwargs={"station_id": station.id})
    return HttpResponseRedirect(redirect_url)

def mini_graphs(request, station_id):
    station = Station.objects.get(pk=station_id)
    if station.cdecstation:
        cdecstation = station.cdecstation
        cdecstation.update_sensor_list()
        cdecstation.update_sensor_data()
    redirect_url = reverse("show_station", kwargs={"station_id": station.id})
    return HttpResponseRedirect(redirect_url)
