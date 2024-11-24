from django.contrib import admin

from collector.models import Settlement, Forecast, ForecastDifference


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Settlement._meta.fields if field.name != "id"]

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
        list_display = [field.name for field in Forecast._meta.fields if field.name != "id"]

@admin.register(ForecastDifference)
class ForecastDifferenceAdmin(admin.ModelAdmin):
        list_display = [field.name for field in ForecastDifference._meta.fields if field.name != "id"]
