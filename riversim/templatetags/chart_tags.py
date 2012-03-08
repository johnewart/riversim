__author__ = 'jewart'
from django import template

from riversim.models import *

register = template.Library()

def sensor_chart(sensor_id):
    sensor = Sensor.objects.get(pk=sensor_id)
    return {'sensor': sensor}


register.inclusion_tag('riversim/tags/sensor_chart.html')(sensor_chart)
