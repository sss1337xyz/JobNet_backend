from django.forms import ModelForm
from .models import Services


class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = ['user', 'title', 'image', 'description', 'price', 'requirements']