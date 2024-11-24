from django.urls import path
from collector.views import insert_forecast

app_name = 'collector'

urlpatterns = [
    path('insert', insert_forecast),
]