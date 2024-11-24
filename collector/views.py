import json
from django.http import JsonResponse

from WFSR.decorators.methods import post_method
from collector.forms import ForecastModel


@post_method
def insert_forecast(request):
    form = ForecastModel(json.loads(request.body))

    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse(form.errors, status=400)