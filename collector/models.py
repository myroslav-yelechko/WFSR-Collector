from django.db import models


class Settlement(models.Model):
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class ForecastBase(models.Model):
    class Meta:
        abstract = True

    comparable = [
        'air_temperature',
        'weather',
    ]

    air_temperature = models.FloatField(blank=True, null=True)
    weather = models.TextField(blank=True, null=True)


class Forecast(ForecastBase):
    class Meta:
        indexes = [
            models.Index(fields=['time'], name='time'),
        ]

    time = models.DateTimeField()
    settlement = models.ForeignKey(Settlement, on_delete=models.PROTECT)

    @staticmethod
    def compare(original, to_compare):
        changed = {}
        for c in ForecastBase.comparable:
            if original.__dict__.get(c) != to_compare.__dict__.get(c):
                changed[c] = to_compare.__dict__.get(c)

        return changed


class ForecastDifference(ForecastBase):
        updated_at = models.DateTimeField()
        forecast = models.ForeignKey(Forecast, on_delete=models.PROTECT)
