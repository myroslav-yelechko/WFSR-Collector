from django.core.management import call_command
from django.test import TestCase, Client

from collector.models import Forecast


class ForecastTestCase(TestCase):
    fixtures = ['settlements', 'forecasts']

    def setUp(self):
        self.client = Client()

        self.created_forecasts = [
            Forecast.objects.create(settlement_id=3, time="2024-11-17T18:00:00Z", air_temperature=2.3,
                                    weather='cloudy'),
            Forecast.objects.create(settlement_id=7, time="2024-11-17T19:00:00Z", air_temperature=2.7, weather='rainy'),
            Forecast.objects.create(settlement_id=7, time="2024-11-17T20:00:00Z", air_temperature=2.8, weather='rainy')
        ]

    def test_find(self):
        times = ["2024-11-17T18:00:00Z", "2024-11-17T19:00:00Z", "2024-11-17T20:00:00Z"]
        forecasts = Forecast.objects.filter(time__in=times, settlement_id=7).all()

        self.assertEqual(len(forecasts), 2)

    def test_inserting(self):
        model = {
            'time': "2024-08-13T12:00:00Z",
            'air_temperature': 11.2,
            'weather': 'rainy',
            'settlement': 2,
        }

        response = self.client.post('/collector/insert', content_type='application/json', data=model)
        self.assertEqual(response.status_code, 200)

        forecast = Forecast.objects.get(time=model['time'], settlement_id=model['settlement'])
        self.assertTrue(forecast)
        self.assertEqual(forecast.air_temperature, model['air_temperature'])
        self.assertEqual(forecast.weather, model['weather'])

    def test_job(self):
        # test of collect job, for debugging
        result = call_command('collect', lt=5)
        self.assertEqual(result, "Job was successfully done")