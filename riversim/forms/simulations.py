__author__ = 'jewart'

from django.forms import ModelForm
from riversim.models import *

class EditSimulationForm(ModelForm):
    class Meta:
        model = Simulation