from django.contrib import admin

# Register your models here.
from .models import Device, Measurement

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('serial', 'name', 'user', 'creation_date')
    search_fields = ('name', 'user__username', 'serial')
    list_filter = ('creation_date',)
    ordering = ('-creation_date',)

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('device', 'values', 'timestamp')
    search_fields = ('device','timestamp')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)