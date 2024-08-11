from django.forms import ModelForm
from .models import *

class DealCreationForm(ModelForm):
    class Meta:
        model = Form
        fields = ['name', 'email', 'deal', 'note']

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['apitoken', 'baseurl', 'userid']
