from django.template import RequestContext

from django.shortcuts import render_to_response
from django.http import HttpResponse

from riversim.models import *

from riversim.shortcuts import log_traceback


def create(request):
    return HttpResponse(status=200)


def update(request, model_id):
    return HttpResponse(status=200)


def edit(request, model_id):
    model = SimulationModel.objects.get(pk=model_id)
    model_parameters = model.modelparameter_set.all()

    params = {
        'model': model,
        'model_parameters': model_parameters
    }

    return render_to_response('riversim/models/edit.html', params, context_instance=RequestContext(request))


def new(request):
    return HttpResponse(status=200)


def list(request):
    models = SimulationModel.objects.all()

    params = {
        'models': models
    }
    return render_to_response('riversim/models/list.html', params, context_instance=RequestContext(request))


def show(request, model_id):
    model = SimulationModel.objects.get(pk=model_id)
    model_parameters = model.modelparameter_set.all()

    params = {
        'model': model,
        'model_parameters': model_parameters
    }

    return render_to_response('riversim/models/show.html', params, context_instance=RequestContext(request))


def edit_parameter(request, model_parameter_id):
    return HttpResponse(status=200)


def create_parameter(request, model_id):
    try:
        model = SimulationModel.objects.get(pk=model_id)

        create_params = {
            'name': request.POST.get("model_parameter['name']"),
            'short_name': request.POST.get("model_parameter['short_name']"),
            'description': request.POST.get("model_parameter['description']"),
            'units': request.POST.get("model_parameter['units']"),
            'model_id': model.id
        }

        logging.debug(create_params)
        model_parameter = ModelParameter.objects.create(**create_params)
        return HttpResponse(status=200)
    except Exception, args:
        log_traceback(Exception, args)