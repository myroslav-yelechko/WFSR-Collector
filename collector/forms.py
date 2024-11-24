from django import forms

from collector.models import Forecast


class ForecastModel(forms.ModelForm):
    class Meta:
        model = Forecast
        fields = '__all__'