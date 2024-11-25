import math
import os
import time
import datetime
import requests
import logging

from celery.utils.log import get_task_logger
from django.core.cache import caches

from collector.models import Settlement, Forecast, ForecastDifference

system_logger = logging.getLogger('system')
benchmark_logger = logging.getLogger('benchmark')
celery_logger = get_task_logger(__name__)
collect_forecast_cache = caches['default']

last_modified_prefix = 'lm'
expires_prefix = 'exp'

def job(lt: int = None):
    # This job is gathering forecasts for future analyze
    # collect forecasts for all settlements -> transform collected data -> gather
    # current data from db -> compare every fields by date -> store all the differences in database

    time_start = time.perf_counter()
    consecutive_error_happened = False
    send_release_update_message = True

    try:
        # lt for tests
        settlements = Settlement.objects.all() if lt is None else Settlement.objects.filter(id__lt=lt)
        for index, settlement in enumerate(settlements):
            # monitoring
            if (index + 1) % math.floor(len(settlements) / 10) == 0:
                percent = math.ceil(((index + 1) / len(settlements)) * 100)
                celery_logger.info("{percent}% of job is ready".format(percent=percent))

            # check if current data expired
            expires = collect_forecast_cache.get(get_exp_key(settlement))
            if expires is not None and datetime.datetime.strptime(expires, "%a, %d %b %Y %H:%M:%S GMT") > datetime.datetime.utcnow():
                continue

            query = '?lat={lat}&lon={lon}'.format(lat=settlement.latitude,
                                                  lon=settlement.longitude)

            try:
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'User-Agent': os.getenv("WEATHER_USER_AGENT"),
                }

                if_modified_since = collect_forecast_cache.get(get_lm_key(settlement))
                if if_modified_since is not None:
                    headers['If-Modified-Since'] = if_modified_since

                response = requests.get(
                    os.getenv("WEATHER_API_URL") + query,
                    headers=headers
                )

                if 200 <= response.status_code < 300:
                    if response.headers.get('Last-Modified'):
                        collect_forecast_cache.set(get_lm_key(settlement), response.headers['Last-Modified'])
                    if response.headers.get('Expires'):
                        collect_forecast_cache.set(get_exp_key(settlement), response.headers['Expires'])

                    response_json = response.json()
                    props = response_json['properties']
                    updated_at = props['meta']['updated_at']
                    timeseries = props['timeseries']

                    timeseries_models = list(map(timeserie_to_forecast, timeseries))
                    forecasts = retrieve_forecasts(list(map(lambda t: t['time'], timeseries)), settlement)

                    for to_compare in timeseries_models:
                        original = forecasts.get(to_compare.time)

                        if original:
                            changed = Forecast.compare(original, to_compare)

                            if len(changed):
                                ForecastDifference(
                                    **changed,
                                    updated_at=updated_at,
                                    forecast=original
                                ).save()
                        else:
                            to_compare.settlement = settlement
                            to_compare.save()

                    consecutive_error_happened = False
                    # sleep to make flat network traffic
                    time.sleep(1)

                if response.status_code == 203 and os.getenv("WEATHER_IGNORE_UPDATE_MESSAGE") == 'False':
                    if send_release_update_message:
                        system_logger.error("The new version of API was released!")
                        send_release_update_message = False

                if response.status_code >= 400:
                    raise response.raise_for_status()

            except requests.exceptions.RequestException as e:
                # Do not want to break if it is network exception
                if consecutive_error_happened:
                    system_logger.critical("Job was forced to end due to consecutive error\n" + str(e),
                                           exc_info=True)
                    return "Critical problem occurred"
                consecutive_error_happened = True
                system_logger.error(e, exc_info=True)
    except Exception as e:
        system_logger.critical(e, exc_info=True)
        return "Critical problem occurred"

    time_end = time.perf_counter()
    benchmark_logger.info("Cron job was done in {minutes} minutes".format(minutes=time.strftime("%M:%S", time.gmtime(time_end - time_start))))
    return "Job was successfully done"

def get_lm_key(settlement):
    return last_modified_prefix + str(settlement.id)

def get_exp_key(settlement):
    return expires_prefix + str(settlement.id)

def timeserie_to_forecast(t):
    fields = {
        'time': datetime.datetime.fromisoformat(t['time']),
        'air_temperature': t['data']['instant']['details']['air_temperature'],
    }

    if t['data'].get('next_1_hours'):
        fields['weather'] = t['data']['next_1_hours']['summary']['symbol_code']

    return Forecast(**fields)


def retrieve_forecasts(times, settlement) -> dict[str:Forecast]:
    forecasts = list(Forecast.objects.filter(time__in=times, settlement=settlement))
    models = {}

    for forecast in forecasts:
        models[forecast.time] = forecast

    return models
